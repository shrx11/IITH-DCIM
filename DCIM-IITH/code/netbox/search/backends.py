from collections import defaultdict

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.models import F, Window, Q
from django.db.models.functions import window
from django.db.models.signals import post_delete, post_save
from django.utils.module_loading import import_string
import netaddr
from netaddr.core import AddrFormatError

from extras.models import CachedValue, CustomField
from netbox.registry import registry
from utilities.querysets import RestrictedPrefetch
from utilities.utils import title
from . import FieldTypes, LookupTypes, get_indexer

DEFAULT_LOOKUP_TYPE = LookupTypes.PARTIAL
MAX_RESULTS = 1000


class SearchBackend:
    """
    Base class for search backends. Subclasses must extend the `cache()`, `remove()`, and `clear()` methods below.
    """
    _object_types = None

    def get_object_types(self):
        """
        Return a list of all registered object types, organized by category, suitable for populating a form's
        ChoiceField.
        """
        if not self._object_types:

            # Organize choices by category
            categories = defaultdict(dict)
            for label, idx in registry['search'].items():
                categories[idx.get_category()][label] = title(idx.model._meta.verbose_name)

            # Compile a nested tuple of choices for form rendering
            results = (
                ('', 'All Objects'),
                *[(category, list(choices.items())) for category, choices in categories.items()]
            )

            self._object_types = results

        return self._object_types

    def search(self, value, user=None, object_types=None, lookup=DEFAULT_LOOKUP_TYPE):
        """
        Search cached object representations for the given value.
        """
        raise NotImplementedError

    def caching_handler(self, sender, instance, created, **kwargs):
        """
        Receiver for the post_save signal, responsible for caching object creation/changes.
        """
        self.cache(instance, remove_existing=not created)

    def removal_handler(self, sender, instance, **kwargs):
        """
        Receiver for the post_delete signal, responsible for caching object deletion.
        """
        self.remove(instance)

    def cache(self, instances, indexer=None, remove_existing=True):
        """
        Create or update the cached representation of an instance.
        """
        raise NotImplementedError

    def remove(self, instance):
        """
        Delete any cached representation of an instance.
        """
        raise NotImplementedError

    def clear(self, object_types=None):
        """
        Delete *all* cached data (optionally filtered by object type).
        """
        raise NotImplementedError

    def count(self, object_types=None):
        """
        Return a count of all cache entries (optionally filtered by object type).
        """
        raise NotImplementedError

    @property
    def size(self):
        """
        Return a total number of cached entries. The meaning of this value will be
        backend-dependent.
        """
        return None


class CachedValueSearchBackend(SearchBackend):

    def search(self, value, user=None, object_types=None, lookup=DEFAULT_LOOKUP_TYPE):

        query_filter = Q(**{f'value__{lookup}': value})

        if object_types:
            query_filter &= Q(object_type__in=object_types)

        if lookup in (LookupTypes.STARTSWITH, LookupTypes.ENDSWITH):
            # Partial string matches are valid only on string values
            query_filter &= Q(type=FieldTypes.STRING)

        if lookup == LookupTypes.PARTIAL:
            try:
                address = str(netaddr.IPNetwork(value.strip()).cidr)
                query_filter |= Q(type=FieldTypes.CIDR) & Q(value__net_contains_or_equals=address)
            except (AddrFormatError, ValueError):
                pass

        # Construct the base queryset to retrieve matching results
        queryset = CachedValue.objects.filter(query_filter).annotate(
            # Annotate the rank of each result for its object according to its weight
            row_number=Window(
                expression=window.RowNumber(),
                partition_by=[F('object_type'), F('object_id')],
                order_by=[F('weight').asc()],
            )
        )[:MAX_RESULTS]

        # Construct a Prefetch to pre-fetch only those related objects for which the
        # user has permission to view.
        if user:
            prefetch = (RestrictedPrefetch('object', user, 'view'), 'object_type')
        else:
            prefetch = ('object', 'object_type')

        # Wrap the base query to return only the lowest-weight result for each object
        # Hat-tip to https://blog.oyam.dev/django-filter-by-window-function/ for the solution
        sql, params = queryset.query.sql_with_params()
        results = CachedValue.objects.prefetch_related(*prefetch).raw(
            f"SELECT * FROM ({sql}) t WHERE row_number = 1",
            params
        )

        # Omit any results pertaining to an object the user does not have permission to view
        return [
            r for r in results if r.object is not None
        ]

    def cache(self, instances, indexer=None, remove_existing=True):
        content_type = None
        custom_fields = None

        # Convert a single instance to an iterable
        if not hasattr(instances, '__iter__'):
            instances = [instances]

        buffer = []
        counter = 0
        for instance in instances:

            # First item
            if not counter:

                # Determine the indexer
                if indexer is None:
                    try:
                        indexer = get_indexer(instance)
                    except KeyError:
                        break

                # Prefetch any associated custom fields
                content_type = ContentType.objects.get_for_model(indexer.model)
                custom_fields = CustomField.objects.filter(content_types=content_type).exclude(search_weight=0)

            # Wipe out any previously cached values for the object
            if remove_existing:
                self.remove(instance)

            # Generate cache data
            for field in indexer.to_cache(instance, custom_fields=custom_fields):
                buffer.append(
                    CachedValue(
                        object_type=content_type,
                        object_id=instance.pk,
                        field=field.name,
                        type=field.type,
                        weight=field.weight,
                        value=field.value
                    )
                )

            # Check whether the buffer needs to be flushed
            if len(buffer) >= 2000:
                counter += len(CachedValue.objects.bulk_create(buffer))
                buffer = []

        # Final buffer flush
        if buffer:
            counter += len(CachedValue.objects.bulk_create(buffer))

        return counter

    def remove(self, instance):
        # Avoid attempting to query for non-cacheable objects
        try:
            get_indexer(instance)
        except KeyError:
            return

        ct = ContentType.objects.get_for_model(instance)
        qs = CachedValue.objects.filter(object_type=ct, object_id=instance.pk)

        # Call _raw_delete() on the queryset to avoid first loading instances into memory
        return qs._raw_delete(using=qs.db)

    def clear(self, object_types=None):
        qs = CachedValue.objects.all()
        if object_types:
            qs = qs.filter(object_type__in=object_types)

        # Call _raw_delete() on the queryset to avoid first loading instances into memory
        return qs._raw_delete(using=qs.db)

    def count(self, object_types=None):
        qs = CachedValue.objects.all()
        if object_types:
            qs = qs.filter(object_type__in=object_types)
        return qs.count()

    @property
    def size(self):
        return CachedValue.objects.count()


def get_backend():
    """
    Initializes and returns the configured search backend.
    """
    try:
        backend_cls = import_string(settings.SEARCH_BACKEND)
    except AttributeError:
        raise ImproperlyConfigured(f"Failed to import configured SEARCH_BACKEND: {settings.SEARCH_BACKEND}")

    # Initialize and return the backend instance
    return backend_cls()


search_backend = get_backend()

# Connect handlers to the appropriate model signals
post_save.connect(search_backend.caching_handler)
post_delete.connect(search_backend.removal_handler)

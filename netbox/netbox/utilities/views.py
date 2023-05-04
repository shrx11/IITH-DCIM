from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from netbox.registry import registry
from .permissions import resolve_permission

__all__ = (
    'ContentTypePermissionRequiredMixin',
    'GetReturnURLMixin',
    'ObjectPermissionRequiredMixin',
    'ViewTab',
    'register_model_view',
)


#
# View Mixins
#

class ContentTypePermissionRequiredMixin(AccessMixin):
    """
    Similar to Django's built-in PermissionRequiredMixin, but extended to check model-level permission assignments.
    This is related to ObjectPermissionRequiredMixin, except that is does not enforce object-level permissions,
    and fits within NetBox's custom permission enforcement system.

    additional_permissions: An optional iterable of statically declared permissions to evaluate in addition to those
                            derived from the object type
    """
    additional_permissions = list()

    def get_required_permission(self):
        """
        Return the specific permission necessary to perform the requested action on an object.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_required_permission()")

    def has_permission(self):
        user = self.request.user
        permission_required = self.get_required_permission()

        # Check that the user has been granted the required permission(s).
        if user.has_perms((permission_required, *self.additional_permissions)):
            return True

        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class ObjectPermissionRequiredMixin(AccessMixin):
    """
    Similar to Django's built-in PermissionRequiredMixin, but extended to check for both model-level and object-level
    permission assignments. If the user has only object-level permissions assigned, the view's queryset is filtered
    to return only those objects on which the user is permitted to perform the specified action.

    additional_permissions: An optional iterable of statically declared permissions to evaluate in addition to those
                            derived from the object type
    """
    additional_permissions = list()

    def get_required_permission(self):
        """
        Return the specific permission necessary to perform the requested action on an object.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_required_permission()")

    def has_permission(self):
        user = self.request.user
        permission_required = self.get_required_permission()

        # Check that the user has been granted the required permission(s).
        if user.has_perms((permission_required, *self.additional_permissions)):

            # Update the view's QuerySet to filter only the permitted objects
            action = resolve_permission(permission_required)[1]
            self.queryset = self.queryset.restrict(user, action)

            return True

        return False

    def dispatch(self, request, *args, **kwargs):

        if not hasattr(self, 'queryset'):
            raise ImproperlyConfigured(
                '{} has no queryset defined. ObjectPermissionRequiredMixin may only be used on views which define '
                'a base queryset'.format(self.__class__.__name__)
            )

        if not self.has_permission():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class GetReturnURLMixin:
    """
    Provides logic for determining where a user should be redirected after processing a form.
    """
    default_return_url = None

    def get_return_url(self, request, obj=None):

        # First, see if `return_url` was specified as a query parameter or form data. Use this URL only if it's
        # considered safe.
        return_url = request.GET.get('return_url') or request.POST.get('return_url')
        if return_url and return_url.startswith('/'):
            return return_url

        # Next, check if the object being modified (if any) has an absolute URL.
        if obj is not None and obj.pk and hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()

        # Fall back to the default URL (if specified) for the view.
        if self.default_return_url is not None:
            return reverse(self.default_return_url)

        # Attempt to dynamically resolve the list view for the object
        if hasattr(self, 'queryset'):
            model_opts = self.queryset.model._meta
            try:
                return reverse(f'{model_opts.app_label}:{model_opts.model_name}_list')
            except NoReverseMatch:
                pass

        # If all else fails, return home. Ideally this should never happen.
        return reverse('home')


class ViewTab:
    """
    ViewTabs are used for navigation among multiple object-specific views, such as the changelog or journal for
    a particular object.

    Args:
        label: Human-friendly text
        badge: A static value or callable to display alongside the label (optional). If a callable is used, it must
            accept a single argument representing the object being viewed.
        weight: Numeric weight to influence ordering among other tabs (default: 1000)
        permission: The permission required to display the tab (optional).
        hide_if_empty: If true, the tab will be displayed only if its badge has a meaningful value. (Tabs without a
            badge are always displayed.)
    """
    def __init__(self, label, badge=None, weight=1000, permission=None, hide_if_empty=False):
        self.label = label
        self.badge = badge
        self.weight = weight
        self.permission = permission
        self.hide_if_empty = hide_if_empty

    def render(self, instance):
        """Return the attributes needed to render a tab in HTML."""
        badge_value = self._get_badge_value(instance)
        if self.badge and self.hide_if_empty and not badge_value:
            return None
        return {
            'label': self.label,
            'badge': badge_value,
            'weight': self.weight,
        }

    def _get_badge_value(self, instance):
        if not self.badge:
            return None
        if callable(self.badge):
            return self.badge(instance)
        return self.badge


def register_model_view(model, name='', path=None, kwargs=None):
    """
    This decorator can be used to "attach" a view to any model in NetBox. This is typically used to inject
    additional tabs within a model's detail view. For example, to add a custom tab to NetBox's dcim.Site model:

        @netbox_model_view(Site, 'myview', path='my-custom-view')
        class MyView(ObjectView):
            ...

    This will automatically create a URL path for MyView at `/dcim/sites/<id>/my-custom-view/` which can be
    resolved using the view name `dcim:site_myview'.

    Args:
        model: The Django model class with which this view will be associated.
        name: The string used to form the view's name for URL resolution (e.g. via `reverse()`). This will be appended
            to the name of the base view for the model using an underscore. If blank, the model name will be used.
        path: The URL path by which the view can be reached (optional). If not provided, `name` will be used.
        kwargs: A dictionary of keyword arguments for the view to include when registering its URL path (optional).
    """
    def _wrapper(cls):
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        if model_name not in registry['views'][app_label]:
            registry['views'][app_label][model_name] = []

        registry['views'][app_label][model_name].append({
            'name': name,
            'view': cls,
            'path': path or name,
            'kwargs': kwargs or {},
        })

        return cls

    return _wrapper

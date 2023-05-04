import logging

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.db.models import ProtectedError
from rest_framework import mixins as drf_mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utilities.exceptions import AbortRequest
from . import mixins

__all__ = (
    'NetBoxReadOnlyModelViewSet',
    'NetBoxModelViewSet',
)

HTTP_ACTIONS = {
    'GET': 'view',
    'OPTIONS': None,
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


class BaseViewSet(GenericViewSet):
    """
    Base class for all API ViewSets. This is responsible for the enforcement of object-based permissions.
    """
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        # Restrict the view's QuerySet to allow only the permitted objects
        if request.user.is_authenticated:
            if action := HTTP_ACTIONS[request.method]:
                self.queryset = self.queryset.restrict(request.user, action)


class NetBoxReadOnlyModelViewSet(
    mixins.BriefModeMixin,
    mixins.CustomFieldsMixin,
    mixins.ExportTemplatesMixin,
    drf_mixins.RetrieveModelMixin,
    drf_mixins.ListModelMixin,
    BaseViewSet
):
    pass


class NetBoxModelViewSet(
    mixins.BulkUpdateModelMixin,
    mixins.BulkDestroyModelMixin,
    mixins.ObjectValidationMixin,
    mixins.BriefModeMixin,
    mixins.CustomFieldsMixin,
    mixins.ExportTemplatesMixin,
    drf_mixins.CreateModelMixin,
    drf_mixins.RetrieveModelMixin,
    drf_mixins.UpdateModelMixin,
    drf_mixins.DestroyModelMixin,
    drf_mixins.ListModelMixin,
    BaseViewSet
):
    """
    Extend DRF's ModelViewSet to support bulk update and delete functions.
    """
    def get_object_with_snapshot(self):
        """
        Save a pre-change snapshot of the object immediately after retrieving it. This snapshot will be used to
        record the "before" data in the changelog.
        """
        obj = super().get_object()
        if hasattr(obj, 'snapshot'):
            obj.snapshot()
        return obj

    def get_serializer(self, *args, **kwargs):
        # If a list of objects has been provided, initialize the serializer with many=True
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')

        try:
            return super().dispatch(request, *args, **kwargs)
        except ProtectedError as e:
            protected_objects = list(e.protected_objects)
            msg = f'Unable to delete object. {len(protected_objects)} dependent objects were found: '
            msg += ', '.join([f'{obj} ({obj.pk})' for obj in protected_objects])
            logger.warning(msg)
            return self.finalize_response(
                request,
                Response({'detail': msg}, status=409),
                *args,
                **kwargs
            )
        except AbortRequest as e:
            logger.debug(e.message)
            return self.finalize_response(
                request,
                Response({'detail': e.message}, status=400),
                *args,
                **kwargs
            )

    # Creates

    def perform_create(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')
        logger.info(f"Creating new {model._meta.verbose_name}")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic():
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    # Updates

    def update(self, request, *args, **kwargs):
        # Hotwire get_object() to ensure we save a pre-change snapshot
        self.get_object = self.get_object_with_snapshot
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        model = self.queryset.model
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')
        logger.info(f"Updating {model._meta.verbose_name} {serializer.instance} (PK: {serializer.instance.pk})")

        # Enforce object-level permissions on save()
        try:
            with transaction.atomic():
                instance = serializer.save()
                self._validate_objects(instance)
        except ObjectDoesNotExist:
            raise PermissionDenied()

    # Deletes

    def destroy(self, request, *args, **kwargs):
        # Hotwire get_object() to ensure we save a pre-change snapshot
        self.get_object = self.get_object_with_snapshot
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        model = self.queryset.model
        logger = logging.getLogger(f'netbox.api.views.{self.__class__.__name__}')
        logger.info(f"Deleting {model._meta.verbose_name} {instance} (PK: {instance.pk})")

        return super().perform_destroy(instance)

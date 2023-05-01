import socket

from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ViewSet

from dcim import filtersets
from dcim.models import *
from extras.api.views import ConfigContextQuerySetMixin
from netbox.api.authentication import IsAuthenticatedOrLoginNotRequired
from netbox.api.exceptions import ServiceUnavailable
from netbox.api.metadata import ContentTypeMetadata
from netbox.api.pagination import StripCountAnnotationsPaginator
from netbox.api.viewsets import NetBoxModelViewSet
from netbox.config import get_config
from netbox.constants import NESTED_SERIALIZER_PREFIX
from utilities.api import get_serializer_for_model
from utilities.utils import count_related
from . import serializers
from .exceptions import MissingFilterException


class DCIMRootView(APIRootView):
    """
    DCIM API root view
    """
    def get_view_name(self):
        return 'DCIM'


# Mixins

class PathEndpointMixin(object):

    @action(detail=True, url_path='trace')
    def trace(self, request, pk):
        """
        Trace a complete cable path and return each segment as a three-tuple of (termination, cable, termination).
        """
        obj = get_object_or_404(self.queryset, pk=pk)

        # Initialize the path array
        path = []

        # Serialize path objects, iterating over each three-tuple in the path
        for near_ends, cable, far_ends in obj.trace():
            if near_ends:
                serializer_a = get_serializer_for_model(near_ends[0], prefix=NESTED_SERIALIZER_PREFIX)
                near_ends = serializer_a(near_ends, many=True, context={'request': request}).data
            else:
                # Path is split; stop here
                break
            if cable:
                cable = serializers.TracedCableSerializer(cable[0], context={'request': request}).data
            if far_ends:
                serializer_b = get_serializer_for_model(far_ends[0], prefix=NESTED_SERIALIZER_PREFIX)
                far_ends = serializer_b(far_ends, many=True, context={'request': request}).data

            path.append((near_ends, cable, far_ends))

        return Response(path)


#
# Departments
#

class DepartmentViewSet(NetBoxModelViewSet):
    queryset = Department.objects.add_related_count(
        Department.objects.all(),
        Lab,
        'group',
        'lab_count',
        cumulative=True
    ).prefetch_related('tags')
    serializer_class = serializers.DepartmentSerializer
    filterset_class = filtersets.DepartmentFilterSet


#
# Labs
#

class LabViewSet(NetBoxModelViewSet):
    queryset = Lab.objects.prefetch_related(
        'region', 'tenant', 'asns', 'tags'
    ).annotate(
        device_count=count_related(Device, 'lab'),
    )
    serializer_class = serializers.LabSerializer
    filterset_class = filtersets.LabFilterSet

#
# Manufacturers
#

class ManufacturerViewSet(NetBoxModelViewSet):
    queryset = Manufacturer.objects.prefetch_related('tags').annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer'),
    )
    serializer_class = serializers.ManufacturerSerializer
    filterset_class = filtersets.ManufacturerFilterSet


#
# Device/module types
#

class DeviceTypeViewSet(NetBoxModelViewSet):
    queryset = DeviceType.objects.prefetch_related('manufacturer', 'tags').annotate(
        device_count=count_related(Device, 'device_type')
    )
    serializer_class = serializers.DeviceTypeSerializer
    filterset_class = filtersets.DeviceTypeFilterSet
    brief_prefetch_fields = ['manufacturer']


#
# Device roles
#

class DeviceRoleViewSet(NetBoxModelViewSet):
    queryset = DeviceRole.objects.prefetch_related('tags').annotate(
        device_count=count_related(Device, 'device_role'),
    )
    serializer_class = serializers.DeviceRoleSerializer
    filterset_class = filtersets.DeviceRoleFilterSet




#
# Devices/modules
#

class DeviceViewSet(ConfigContextQuerySetMixin, NetBoxModelViewSet):
    queryset = Device.objects.prefetch_related(
        'device_type__manufacturer', 'device_role', 'tenant', 'platform', 'lab', 'location', 'rack', 'parent_bay',
        'virtual_chassis__master', 'primary_ip4__nat_outside', 'primary_ip6__nat_outside', 'tags',
    )
    filterset_class = filtersets.DeviceFilterSet
    pagination_class = StripCountAnnotationsPaginator

    def get_serializer_class(self):
        """
        Select the specific serializer based on the request context.

        If the `brief` query param equates to True, return the NestedDeviceSerializer

        If the `exclude` query param includes `config_context` as a value, return the DeviceSerializer

        Else, return the DeviceWithConfigContextSerializer
        """

        request = self.get_serializer_context()['request']
        if request.query_params.get('brief', False):
            return serializers.NestedDeviceSerializer

        elif 'config_context' in request.query_params.get('exclude', []):
            return serializers.DeviceSerializer

        return serializers.DeviceWithConfigContextSerializer

    @swagger_auto_schema(
        manual_parameters=[
            Parameter(
                name='method',
                in_='query',
                required=True,
                type=openapi.TYPE_STRING
            )
        ],
        responses={'200': serializers.DeviceNAPALMSerializer}
    )
    @action(detail=True, url_path='napalm')
    def napalm(self, request, pk):
        """
        Execute a NAPALM method on a Device
        """
        device = get_object_or_404(self.queryset, pk=pk)
        if not device.primary_ip:
            raise ServiceUnavailable("This device does not have a primary IP address configured.")
        if device.platform is None:
            raise ServiceUnavailable("No platform is configured for this device.")
        if not device.platform.napalm_driver:
            raise ServiceUnavailable(f"No NAPALM driver is configured for this device's platform: {device.platform}.")

        # Check for primary IP address from NetBox object
        if device.primary_ip:
            host = str(device.primary_ip.address.ip)
        else:
            # Raise exception for no IP address and no Name if device.name does not exist
            if not device.name:
                raise ServiceUnavailable(
                    "This device does not have a primary IP address or device name to lookup configured."
                )
            try:
                # Attempt to complete a DNS name resolution if no primary_ip is set
                host = socket.gethostbyname(device.name)
            except socket.gaierror:
                # Name lookup failure
                raise ServiceUnavailable(
                    f"Name lookup failure, unable to resolve IP address for {device.name}. Please set Primary IP or "
                    f"setup name resolution.")

        # Check that NAPALM is installed
        try:
            import napalm
            from napalm.base.exceptions import ModuleImportError
        except ModuleNotFoundError as e:
            if getattr(e, 'name') == 'napalm':
                raise ServiceUnavailable("NAPALM is not installed. Please see the documentation for instructions.")
            raise e

        # Validate the configured driver
        try:
            driver = napalm.get_network_driver(device.platform.napalm_driver)
        except ModuleImportError:
            raise ServiceUnavailable("NAPALM driver for platform {} not found: {}.".format(
                device.platform, device.platform.napalm_driver
            ))

        # Verify user permission
        if not request.user.has_perm('dcim.napalm_read_device'):
            return HttpResponseForbidden()

        napalm_methods = request.GET.getlist('method')
        response = {m: None for m in napalm_methods}

        config = get_config()
        username = config.NAPALM_USERNAME
        password = config.NAPALM_PASSWORD
        timeout = config.NAPALM_TIMEOUT
        optional_args = config.NAPALM_ARGS.copy()
        if device.platform.napalm_args is not None:
            optional_args.update(device.platform.napalm_args)

        # Update NAPALM parameters according to the request headers
        for header in request.headers:
            if header[:9].lower() != 'x-napalm-':
                continue

            key = header[9:]
            if key.lower() == 'username':
                username = request.headers[header]
            elif key.lower() == 'password':
                password = request.headers[header]
            elif key:
                optional_args[key.lower()] = request.headers[header]

        # Connect to the device
        d = driver(
            hostname=host,
            username=username,
            password=password,
            timeout=timeout,
            optional_args=optional_args
        )
        try:
            d.open()
        except Exception as e:
            raise ServiceUnavailable("Error connecting to the device at {}: {}".format(host, e))

        # Validate and execute each specified NAPALM method
        for method in napalm_methods:
            if not hasattr(driver, method):
                response[method] = {'error': 'Unknown NAPALM method'}
                continue
            if not method.startswith('get_'):
                response[method] = {'error': 'Only get_* NAPALM methods are supported'}
                continue
            try:
                response[method] = getattr(d, method)()
            except NotImplementedError:
                response[method] = {'error': 'Method {} not implemented for NAPALM driver {}'.format(method, driver)}
            except Exception as e:
                response[method] = {'error': 'Method {} failed: {}'.format(method, e)}
        d.close()

        return Response(response)

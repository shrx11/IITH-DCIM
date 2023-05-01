import decimal

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from dcim.choices import *
from dcim.models import *

from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import (
    GenericObjectSerializer, NestedGroupModelSerializer, NetBoxModelSerializer, ValidatedModelSerializer,
    WritableNestedSerializer,
)
from netbox.config import ConfigItem
from netbox.constants import NESTED_SERIALIZER_PREFIX
from tenancy.api.nested_serializers import NestedTenantSerializer
from users.api.nested_serializers import NestedUserSerializer
from utilities.api import get_serializer_for_model
from .nested_serializers import *


class DepartmentSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:department-detail')
    parent = NestedDepartmentSerializer(required=False, allow_null=True, default=None)
    lab_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'lab_count', '_depth',
        ]


class LabSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:lab-detail')
    status = ChoiceField(choices=LabStatusChoices, required=False)
    group = NestedDepartmentSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    time_zone = TimeZoneSerializerField(required=False, allow_null=True)

    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lab
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'status', 'region', 'group', 'tenant', 'facility', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated', 'device_count',
        ]


#
# Device/module types
#

class ManufacturerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')
    devicetype_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Manufacturer
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'devicetype_count',
        ]


class DeviceTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer()
    u_height = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        label=_('Position (U)'),
        min_value=0,
        default=1.0
    )
    
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceType
        fields = [
            'id', 'url', 'display', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth',
            'tags', 'custom_fields', 'created', 'last_updated', 'device_count',
        ]

#
# Devices
#

class DeviceRoleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicerole-detail')
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DeviceRole
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'color', 'tags', 'custom_fields',
            'created', 'last_updated', 'device_count',
        ]


class DeviceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')
    device_type = NestedDeviceTypeSerializer()
    device_role = NestedDeviceRoleSerializer()
    tenant = NestedTenantSerializer(required=False, allow_null=True, default=None)
    lab = NestedLabSerializer()
    face = ChoiceField(choices=DeviceFaceChoices, allow_blank=True, default='')
    position = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
        allow_null=True,
        label=_('Position (U)'),
        min_value=decimal.Decimal(0.5),
        default=None
    )
    status = ChoiceField(choices=DeviceStatusChoices, required=False)
    parent_device = serializers.SerializerMethodField()
    vc_position = serializers.IntegerField(allow_null=True, max_value=255, min_value=0, default=None)

    class Meta:
        model = Device
        fields = [
            'id', 'url', 'display', 'name', 'device_type', 'device_role', 'tenant', 'serial',
            'lab', 'rack', 'position', 'face', 'status',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]

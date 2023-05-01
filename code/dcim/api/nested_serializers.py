from rest_framework import serializers

from dcim import models
from netbox.api.serializers import BaseModelSerializer, WritableNestedSerializer

__all__ = [
    'NestedDeviceRoleSerializer',
    'NestedDeviceSerializer',
    'NestedDeviceTypeSerializer',
    'NestedManufacturerSerializer',
    'NestedLabSerializer',
    'NestedDepartmentSerializer',
]


#
# Regions/labs
#

class NestedDepartmentSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:department-detail')
    lab_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.Department
        fields = ['id', 'url', 'display', 'name', 'slug', 'lab_count', '_depth']


class NestedLabSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:lab-detail')

    class Meta:
        model = models.Lab
        fields = ['id', 'url', 'display', 'name', 'slug']


#
# Device/module types
#

class NestedManufacturerSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')
    devicetype_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Manufacturer
        fields = ['id', 'url', 'display', 'name', 'slug', 'devicetype_count']


class NestedDeviceTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer(read_only=True)
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DeviceType
        fields = ['id', 'url', 'display', 'manufacturer', 'model', 'slug', 'device_count']

#
# Devices
#

class NestedDeviceRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicerole-detail')
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DeviceRole
        fields = ['id', 'url', 'display', 'name', 'slug', 'device_count', 'virtualmachine_count']


class NestedDeviceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')

    class Meta:
        model = models.Device
        fields = ['id', 'url', 'display', 'name']
from rest_framework import serializers

from dcim import models
from netbox.api.serializers import BaseModelSerializer, WritableNestedSerializer

__all__ = [
    'ComponentNestedModuleSerializer',
    'ModuleBayNestedModuleSerializer',
    'NestedCableSerializer',
    'NestedConsolePortSerializer',
    'NestedConsolePortTemplateSerializer',
    'NestedConsoleServerPortSerializer',
    'NestedConsoleServerPortTemplateSerializer',
    'NestedDeviceBaySerializer',
    'NestedDeviceBayTemplateSerializer',
    'NestedDeviceRoleSerializer',
    'NestedDeviceSerializer',
    'NestedDeviceTypeSerializer',
    'NestedFrontPortSerializer',
    'NestedFrontPortTemplateSerializer',
    'NestedInterfaceSerializer',
    'NestedInterfaceTemplateSerializer',
    'NestedInventoryItemSerializer',
    'NestedInventoryItemRoleSerializer',
    'NestedInventoryItemTemplateSerializer',
    'NestedManufacturerSerializer',
    'NestedModuleBaySerializer',
    'NestedModuleBayTemplateSerializer',
    'NestedModuleSerializer',
    'NestedModuleTypeSerializer',
    'NestedPlatformSerializer',
    'NestedPowerFeedSerializer',
    'NestedPowerOutletSerializer',
    'NestedPowerOutletTemplateSerializer',
    'NestedPowerPanelSerializer',
    'NestedPowerPortSerializer',
    'NestedPowerPortTemplateSerializer',
    'NestedLocationSerializer',
    'NestedRackReservationSerializer',
    'NestedRackRoleSerializer',
    'NestedRackSerializer',
    'NestedRearPortSerializer',
    'NestedRearPortTemplateSerializer',
    'NestedRegionSerializer',
    'NestedSiteSerializer',
    'NestedSiteGroupSerializer',
    'NestedVirtualChassisSerializer',
    'NestedVirtualDeviceContextSerializer',
]


#
# Regions/sites
#

class NestedRegionSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:region-detail')
    site_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.Region
        fields = ['id', 'url', 'display', 'name', 'slug', 'site_count', '_depth']


class NestedSiteGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:sitegroup-detail')
    site_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.SiteGroup
        fields = ['id', 'url', 'display', 'name', 'slug', 'site_count', '_depth']


class NestedSiteSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:site-detail')

    class Meta:
        model = models.Site
        fields = ['id', 'url', 'display', 'name', 'slug']


#
# Racks
#

class NestedLocationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:location-detail')
    rack_count = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.Location
        fields = ['id', 'url', 'display', 'name', 'slug', 'rack_count', '_depth']


class NestedRackRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackrole-detail')
    rack_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.RackRole
        fields = ['id', 'url', 'display', 'name', 'slug', 'rack_count']


class NestedRackSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rack-detail')
    device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Rack
        fields = ['id', 'url', 'display', 'name', 'device_count']


class NestedRackReservationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackreservation-detail')
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.RackReservation
        fields = ['id', 'url', 'display', 'user', 'units']

    def get_user(self, obj):
        return obj.user.username


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


class NestedModuleTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:moduletype-detail')
    manufacturer = NestedManufacturerSerializer(read_only=True)
    # module_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.ModuleType
        fields = ['id', 'url', 'display', 'manufacturer', 'model']


#
# Component templates
#

class NestedConsolePortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleporttemplate-detail')

    class Meta:
        model = models.ConsolePortTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedConsoleServerPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverporttemplate-detail')

    class Meta:
        model = models.ConsoleServerPortTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedPowerPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerporttemplate-detail')

    class Meta:
        model = models.PowerPortTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedPowerOutletTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlettemplate-detail')

    class Meta:
        model = models.PowerOutletTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedInterfaceTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interfacetemplate-detail')

    class Meta:
        model = models.InterfaceTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedRearPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearporttemplate-detail')

    class Meta:
        model = models.RearPortTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedFrontPortTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontporttemplate-detail')

    class Meta:
        model = models.FrontPortTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedModuleBayTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:modulebaytemplate-detail')

    class Meta:
        model = models.ModuleBayTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedDeviceBayTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebaytemplate-detail')

    class Meta:
        model = models.DeviceBayTemplate
        fields = ['id', 'url', 'display', 'name']


class NestedInventoryItemTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitemtemplate-detail')
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.InventoryItemTemplate
        fields = ['id', 'url', 'display', 'name', '_depth']


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


class NestedPlatformSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Platform
        fields = ['id', 'url', 'display', 'name', 'slug', 'device_count', 'virtualmachine_count']


class NestedDeviceSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')

    class Meta:
        model = models.Device
        fields = ['id', 'url', 'display', 'name']


class ModuleNestedModuleBaySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:modulebay-detail')

    class Meta:
        model = models.ModuleBay
        fields = ['id', 'url', 'display', 'name']


class ModuleBayNestedModuleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:module-detail')

    class Meta:
        model = models.Module
        fields = ['id', 'url', 'display', 'serial']


class ComponentNestedModuleSerializer(WritableNestedSerializer):
    """
    Used by device component serializers.
    """
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:module-detail')
    module_bay = ModuleNestedModuleBaySerializer(read_only=True)

    class Meta:
        model = models.Module
        fields = ['id', 'url', 'display', 'device', 'module_bay']


class NestedModuleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:module-detail')
    device = NestedDeviceSerializer(read_only=True)
    module_bay = ModuleNestedModuleBaySerializer(read_only=True)
    module_type = NestedModuleTypeSerializer(read_only=True)

    class Meta:
        model = models.Module
        fields = ['id', 'url', 'display', 'device', 'module_bay', 'module_type']


class NestedConsoleServerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverport-detail')
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.ConsoleServerPort
        fields = ['id', 'url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedConsolePortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleport-detail')
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.ConsolePort
        fields = ['id', 'url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedPowerOutletSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlet-detail')
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.PowerOutlet
        fields = ['id', 'url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedPowerPortSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerport-detail')
    device = NestedDeviceSerializer(read_only=True)
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.PowerPort
        fields = ['id', 'url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedInterfaceSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.Interface
        fields = ['id', 'url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedRearPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rearport-detail')
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.RearPort
        fields = ['id', 'url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedFrontPortSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:frontport-detail')
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.FrontPort
        fields = ['id', 'url', 'display', 'device', 'name', 'cable', '_occupied']


class NestedModuleBaySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:modulebay-detail')
    module = NestedModuleSerializer(read_only=True)

    class Meta:
        model = models.ModuleBay
        fields = ['id', 'url', 'display', 'module', 'name']


class NestedDeviceBaySerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebay-detail')
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = models.DeviceBay
        fields = ['id', 'url', 'display', 'device', 'name']


class NestedInventoryItemSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitem-detail')
    device = NestedDeviceSerializer(read_only=True)
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = models.InventoryItem
        fields = ['id', 'url', 'display', 'device', 'name', '_depth']


class NestedInventoryItemRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:inventoryitemrole-detail')
    inventoryitem_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.InventoryItemRole
        fields = ['id', 'url', 'display', 'name', 'slug', 'inventoryitem_count']


#
# Cables
#

class NestedCableSerializer(BaseModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:cable-detail')

    class Meta:
        model = models.Cable
        fields = ['id', 'url', 'display', 'label']


#
# Virtual chassis
#

class NestedVirtualChassisSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualchassis-detail')
    master = NestedDeviceSerializer()
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.VirtualChassis
        fields = ['id', 'url', 'display', 'name', 'master', 'member_count']


#
# Power panels/feeds
#

class NestedPowerPanelSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerpanel-detail')
    powerfeed_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.PowerPanel
        fields = ['id', 'url', 'display', 'name', 'powerfeed_count']


class NestedPowerFeedSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerfeed-detail')
    _occupied = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = models.PowerFeed
        fields = ['id', 'url', 'display', 'name', 'cable', '_occupied']


class NestedVirtualDeviceContextSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:virtualdevicecontext-detail')
    device = NestedDeviceSerializer()

    class Meta:
        model = models.VirtualDeviceContext
        fields = ['id', 'url', 'display', 'name', 'identifier', 'device']

from netbox.search import SearchIndex, register_search
from . import models


@register_search
class CableIndex(SearchIndex):
    model = models.Cable
    fields = (
        ('label', 100),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class ConsolePortIndex(SearchIndex):
    model = models.ConsolePort
    fields = (
        ('name', 100),
        ('label', 200),
        ('description', 500),
        ('speed', 2000),
    )


@register_search
class ConsoleServerPortIndex(SearchIndex):
    model = models.ConsoleServerPort
    fields = (
        ('name', 100),
        ('label', 200),
        ('description', 500),
        ('speed', 2000),
    )


@register_search
class DeviceIndex(SearchIndex):
    model = models.Device
    fields = (
        ('asset_tag', 50),
        ('serial', 60),
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class DeviceBayIndex(SearchIndex):
    model = models.DeviceBay
    fields = (
        ('name', 100),
        ('label', 200),
        ('description', 500),
    )


@register_search
class DeviceRoleIndex(SearchIndex):
    model = models.DeviceRole
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class DeviceTypeIndex(SearchIndex):
    model = models.DeviceType
    fields = (
        ('model', 100),
        ('part_number', 200),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class FrontPortIndex(SearchIndex):
    model = models.FrontPort
    fields = (
        ('name', 100),
        ('label', 200),
        ('description', 500),
    )


@register_search
class InterfaceIndex(SearchIndex):
    model = models.Interface
    fields = (
        ('name', 100),
        ('label', 200),
        ('mac_address', 300),
        ('wwn', 300),
        ('description', 500),
        ('mtu', 2000),
        ('speed', 2000),
    )


@register_search
class InventoryItemIndex(SearchIndex):
    model = models.InventoryItem
    fields = (
        ('asset_tag', 50),
        ('serial', 60),
        ('name', 100),
        ('label', 200),
        ('description', 500),
        ('part_id', 2000),
    )


@register_search
class LocationIndex(SearchIndex):
    model = models.Location
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class ManufacturerIndex(SearchIndex):
    model = models.Manufacturer
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class ModuleIndex(SearchIndex):
    model = models.Module
    fields = (
        ('asset_tag', 50),
        ('serial', 60),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class ModuleBayIndex(SearchIndex):
    model = models.ModuleBay
    fields = (
        ('name', 100),
        ('label', 200),
        ('description', 500),
    )


@register_search
class ModuleTypeIndex(SearchIndex):
    model = models.ModuleType
    fields = (
        ('model', 100),
        ('part_number', 200),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class PlatformIndex(SearchIndex):
    model = models.Platform
    fields = (
        ('name', 100),
        ('slug', 110),
        ('napalm_driver', 300),
        ('description', 500),
    )


@register_search
class PowerFeedIndex(SearchIndex):
    model = models.PowerFeed
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class PowerOutletIndex(SearchIndex):
    model = models.PowerOutlet
    fields = (
        ('name', 100),
        ('label', 200),
        ('description', 500),
    )


@register_search
class PowerPanelIndex(SearchIndex):
    model = models.PowerPanel
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class PowerPortIndex(SearchIndex):
    model = models.PowerPort
    fields = (
        ('name', 100),
        ('label', 200),
        ('description', 500),
        ('maximum_draw', 2000),
        ('allocated_draw', 2000),
    )


@register_search
class RackIndex(SearchIndex):
    model = models.Rack
    fields = (
        ('asset_tag', 50),
        ('serial', 60),
        ('name', 100),
        ('facility_id', 200),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class RackReservationIndex(SearchIndex):
    model = models.RackReservation
    fields = (
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class RackRoleIndex(SearchIndex):
    model = models.RackRole
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class RearPortIndex(SearchIndex):
    model = models.RearPort
    fields = (
        ('name', 100),
        ('label', 200),
        ('description', 500),
    )


@register_search
class RegionIndex(SearchIndex):
    model = models.Region
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class SiteIndex(SearchIndex):
    model = models.Site
    fields = (
        ('name', 100),
        ('facility', 100),
        ('slug', 110),
        ('description', 500),
        ('physical_address', 2000),
        ('shipping_address', 2000),
        ('comments', 5000),
    )


@register_search
class SiteGroupIndex(SearchIndex):
    model = models.SiteGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class VirtualChassisIndex(SearchIndex):
    model = models.VirtualChassis
    fields = (
        ('name', 100),
        ('domain', 300),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class VirtualDeviceContextIndex(SearchIndex):
    model = models.VirtualDeviceContext
    fields = (
        ('name', 100),
        ('identifier', 300),
        ('description', 500),
        ('comments', 5000),
    )

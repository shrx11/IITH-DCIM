from netbox.search import SearchIndex, register_search
from . import models


@register_search
class DeviceIndex(SearchIndex):
    model = models.Device
    fields = (
        ('asset_tag', 50),
        ('serial', 60),
        ('name', 100),
        ('comments', 5000),
    )


@register_search
class DeviceRoleIndex(SearchIndex):
    model = models.DeviceRole
    fields = (
        ('name', 100),
        ('slug', 110),
    )


@register_search
class DeviceTypeIndex(SearchIndex):
    model = models.DeviceType
    fields = (
        ('model', 100),
        ('part_number', 200),
        ('comments', 5000),
    )

@register_search
class ManufacturerIndex(SearchIndex):
    model = models.Manufacturer
    fields = (
        ('name', 100),
        ('slug', 110),
    )


@register_search
class LabIndex(SearchIndex):
    model = models.Lab
    fields = (
        ('name', 100),
        ('facility', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class DepartmentIndex(SearchIndex):
    model = models.Department
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
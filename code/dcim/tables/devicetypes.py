import django_tables2 as tables

from dcim import models
from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin

__all__ = (
    'DeviceTypeTable',
    'ManufacturerTable',
)


#
# Manufacturers
#

class ManufacturerTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    devicetype_count = columns.LinkedCountColumn(
        viewname='dcim:devicetype_list',
        url_params={'manufacturer_id': 'pk'},
        verbose_name='Device Types'
    )
    slug = tables.Column()
    tags = columns.TagColumn(
        url_name='dcim:manufacturer_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.Manufacturer
        fields = (
            'pk', 'id', 'name', 'devicetype_count',
            'slug', 'tags', 'contacts', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'devicetype_count',
        )


#
# Device types
#

class DeviceTypeTable(NetBoxTable):
    model = tables.Column(
        linkify=True,
        verbose_name='Device Type'
    )
    manufacturer = tables.Column(
        linkify=True
    )
    is_full_depth = columns.BooleanColumn(
        verbose_name='Full Depth'
    )
    instance_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'device_type_id': 'pk'},
        verbose_name='Instances'
    )
    tags = columns.TagColumn(
        url_name='dcim:devicetype_list'
    )
    u_height = columns.TemplateColumn(
        template_code='{{ value|floatformat }}'
    )

    class Meta(NetBoxTable.Meta):
        model = models.DeviceType
        fields = (
            'pk', 'id', 'model', 'manufacturer', 'slug', 'part_number', 'u_height', 'is_full_depth', 
            'instance_count', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number', 'u_height', 'is_full_depth', 'instance_count',
        )
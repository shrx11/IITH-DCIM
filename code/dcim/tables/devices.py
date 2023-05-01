import django_tables2 as tables
from dcim import models
from django_tables2.utils import Accessor
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from netbox.tables import NetBoxTable, columns

from .template_code import *

__all__ = (
    'DeviceImportTable',
    'DeviceRoleTable',
    'DeviceTable',
)

#
# Device roles
#

class DeviceRoleTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    device_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'role_id': 'pk'},
        verbose_name='Devices'
    )
    color = columns.ColorColumn()
    tags = columns.TagColumn(
        url_name='dcim:devicerole_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.DeviceRole
        fields = (
            'pk', 'id', 'name', 'device_count', 'color', 'slug', 'tags',
            'actions', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'device_count', 'color',)

#
# Devices
#

class DeviceTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    name = tables.TemplateColumn(
        order_by=('_name',),
        template_code=DEVICE_LINK,
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    lab_group = tables.Column(
        accessor=Accessor('department'),
        linkify=True,
        verbose_name='Department'
    )
    lab = tables.Column(
        linkify=True,
        verbose_name="Lab"
    )
    rack = tables.Column(
        linkify=True
    )
    position = columns.TemplateColumn(
        template_code='{{ value|floatformat }}'
    )
    device_role = columns.ColoredLabelColumn(
        verbose_name='Role'
    )
    manufacturer = tables.Column(
        accessor=Accessor('device_type__manufacturer'),
        linkify=True
    )
    device_type = tables.Column(
        linkify=True,
        verbose_name='Type'
    )
    tags = columns.TagColumn(
        url_name='dcim:device_list'
    )

    class Meta(NetBoxTable.Meta):
        model = models.Device
        fields = (
            'pk', 'id', 'name', 'status', 'tenant', 'tenant_group', 'device_role', 'manufacturer', 'device_type',
            'region', 'lab_group', 'lab', 'rack', 'position', 'face',
            'contacts', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'name', 'status', 'lab', 'rack', 'device_type',
        )


class DeviceImportTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.TemplateColumn(
        template_code=DEVICE_LINK,
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    lab = tables.Column(
        linkify=True
    )
    rack = tables.Column(
        linkify=True
    )
    device_role = tables.Column(
        verbose_name='Role'
    )
    device_type = tables.Column(
        verbose_name='Type'
    )

    class Meta(NetBoxTable.Meta):
        model = models.Device
        fields = ('id', 'name', 'status', 'tenant', 'tenant_group', 'lab', 'rack', 'position', 'device_role', 'device_type')
        empty_text = False

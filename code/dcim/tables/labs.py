import django_tables2 as tables
from dcim.models import Location, Region, Lab, Department
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from netbox.tables import NetBoxTable, columns

__all__ = (
    'LocationTable',
    'RegionTable',
    'LabTable',
    'DepartmentTable',
)


#
# Departments
#

class DepartmentTable(ContactsColumnMixin, NetBoxTable):
    name = columns.MPTTColumn(
        linkify=True
    )
    lab_count = columns.LinkedCountColumn(
        viewname='dcim:lab_list',
        url_params={'group_id': 'pk'},
        verbose_name='Labs'
    )
    tags = columns.TagColumn(
        url_name='dcim:department_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Department
        fields = (
            'pk', 'id', 'name', 'slug', 'lab_count', 'description', 'contacts', 'tags', 'created', 'last_updated',
            'actions',
        )
        default_columns = ('pk', 'name', 'lab_count', 'description')


#
# Labs
#

class LabTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    group = tables.Column(
        linkify=True
    )
    tags = columns.TagColumn(
        url_name='dcim:lab_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Lab
        fields = (
            'pk', 'id', 'name', 'slug', 'status', 'facility', 'group', 'tenant', 'tenant_group',
            'time_zone', 'description', 'physical_address', 'shipping_address', 'latitude', 'longitude',
            'contacts', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'status', 'group',)

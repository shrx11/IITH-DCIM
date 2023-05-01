from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from dcim.choices import *
from dcim.models import *
from extras.forms import LocalConfigContextFilterForm
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import ContactModelFilterForm, TenancyFilterForm
from utilities.forms import (
    APISelectMultiple, add_blank_choice, ColorField, DynamicModelMultipleChoiceField, FilterForm, MultipleChoiceField,
    StaticSelect, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES, SelectSpeedWidget,
)

__all__ = (
    'DeviceFilterForm',
    'DeviceRoleFilterForm',
    'DeviceTypeFilterForm',
    'ManufacturerFilterForm',
    'LabFilterForm',
    'DepartmentFilterForm',
)

class DepartmentFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Department
    fieldsets = (
        (None, ('q', 'filter_id', 'tag', 'parent_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group'))
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label=_('Parent group')
    )
    tag = TagFilterField(model)


class LabFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Lab
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        # ('Attributes', ('status', 'region_id', 'group_id', 'asn_id')),
        # ('Tenant', ('tenant_group_id', 'tenant_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
    )
    status = MultipleChoiceField(
        choices=LabStatusChoices,
        required=False
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label=_('Department')
    )
    tag = TagFilterField(model)


class ManufacturerFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Manufacturer
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Contacts', ('contact', 'contact_role', 'contact_group'))
    )
    tag = TagFilterField(model)


class DeviceTypeFilterForm(NetBoxModelFilterSetForm):
    model = DeviceType
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Hardware', ('manufacturer_id', 'part_number',)),
        # ('Images', ('has_front_image', 'has_rear_image')),
        # ('Components', (
        #     'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces',
        #     'pass_through_ports', 'device_bays', 'module_bays', 'inventory_items',
        # )),
        # ('Weight', ('weight', 'weight_unit')),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    part_number = forms.CharField(
        required=False
    )
    subdevice_role = MultipleChoiceField(
        choices=add_blank_choice(SubdeviceRoleChoices),
        required=False
    )
    has_front_image = forms.NullBooleanField(
        required=False,
        label='Has a front image',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    has_rear_image = forms.NullBooleanField(
        required=False,
        label='Has a rear image',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Has console ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Has console server ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Has power ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Has power outlets',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Has interfaces',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Has pass-through ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    device_bays = forms.NullBooleanField(
        required=False,
        label='Has device bays',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    module_bays = forms.NullBooleanField(
        required=False,
        label='Has module bays',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    inventory_items = forms.NullBooleanField(
        required=False,
        label='Has inventory items',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)
    weight = forms.DecimalField(
        required=False
    )


class DeviceRoleFilterForm(NetBoxModelFilterSetForm):
    model = DeviceRole
    tag = TagFilterField(model)


class DeviceFilterForm(
    LocalConfigContextFilterForm,
    TenancyFilterForm,
    ContactModelFilterForm,
    NetBoxModelFilterSetForm
):
    model = Device
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        # ('Location', ('region_id', 'lab_group_id', 'lab_id', 'location_id', 'rack_id')),
        # ('Operation', ('status', 'role_id', 'airflow', 'serial', 'asset_tag', 'mac_address')),
        # ('Hardware', ('manufacturer_id', 'device_type_id', 'platform_id')),
        ('User', ('tenant_group_id', 'tenant_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
        # ('Components', (
        #     'console_ports', 'console_server_ports', 'power_ports', 'power_outlets', 'interfaces', 'pass_through_ports',
        # )),
        # ('Miscellaneous', ('has_primary_ip', 'virtual_chassis_member', 'local_context_data'))
    )
    lab_group_id = DynamicModelMultipleChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label=_('Department')
    )
    lab_id = DynamicModelMultipleChoiceField(
        queryset=Lab.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id',
            'group_id': '$lab_group_id',
        },
        label=_('Lab')
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Role')
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label=_('Manufacturer')
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id'
        },
        label=_('Model')
    )
    status = MultipleChoiceField(
        choices=DeviceStatusChoices,
        required=False
    )
    serial = forms.CharField(
        required=False
    )
    asset_tag = forms.CharField(
        required=False
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label='Has a primary IP',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    virtual_chassis_member = forms.NullBooleanField(
        required=False,
        label='Virtual chassis member',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_ports = forms.NullBooleanField(
        required=False,
        label='Has console ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    console_server_ports = forms.NullBooleanField(
        required=False,
        label='Has console server ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_ports = forms.NullBooleanField(
        required=False,
        label='Has power ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    power_outlets = forms.NullBooleanField(
        required=False,
        label='Has power outlets',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    interfaces = forms.NullBooleanField(
        required=False,
        label='Has interfaces',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    pass_through_ports = forms.NullBooleanField(
        required=False,
        label='Has pass-through ports',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)

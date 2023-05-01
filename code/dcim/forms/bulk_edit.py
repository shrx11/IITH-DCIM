from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from timezone_field import TimeZoneFormField

from dcim.choices import *
from dcim.models import *
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, BulkEditForm, BulkEditNullBooleanSelect, ColorField, CommentField, DynamicModelChoiceField,
    DynamicModelMultipleChoiceField, form_from_model, StaticSelect, SelectSpeedWidget
)

__all__ = (
    'DeviceBulkEditForm',
    'DeviceRoleBulkEditForm',
    'DeviceTypeBulkEditForm',
    'ManufacturerBulkEditForm',
    'LabBulkEditForm',
    'DepartmentBulkEditForm',
)


class DepartmentBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=Department.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = Department
    fieldsets = (
        (None, ('parent', 'description')),
    )
    nullable_fields = ('parent', 'description')


class LabBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        choices=add_blank_choice(LabStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect()
    )
    group = DynamicModelChoiceField(
        queryset=Department.objects.all(),
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    contact_name = forms.CharField(
        max_length=50,
        required=False
    )
    contact_phone = forms.CharField(
        max_length=20,
        required=False
    )
    contact_email = forms.EmailField(
        required=False,
        label=_('Contact E-mail')
    )
    time_zone = TimeZoneFormField(
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False,
        widget=StaticSelect()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Lab
    fieldsets = (
        (None, ('status', 'region', 'group', 'tenant', 'time_zone', 'description')),
    )
    nullable_fields = (
        'region', 'group', 'tenant', 'time_zone', 'description', 'comments',
    )

class ManufacturerBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = Manufacturer
    fieldsets = (
        (None, ('description',)),
    )
    nullable_fields = ('description',)


class DeviceTypeBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    part_number = forms.CharField(
        required=False
    )
    u_height = forms.IntegerField(
        min_value=1,
        required=False
    )
    is_full_depth = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_('Is full depth')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = DeviceType
    fieldsets = (
        ('Device Type', ('manufacturer', 'part_number', 'u_height', 'is_full_depth', 'description')),
        ('Weight', ('weight', 'weight_unit')),
    )
    nullable_fields = ('part_number', 'weight', 'weight_unit', 'description', 'comments')



class DeviceRoleBulkEditForm(NetBoxModelBulkEditForm):
    color = ColorField(
        required=False
    )
    vm_role = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect,
        label=_('VM role')
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    model = DeviceRole
    fieldsets = (
        (None, ('color', 'vm_role', 'description')),
    )
    nullable_fields = ('color', 'description')



class DeviceBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False
    )
    lab = DynamicModelChoiceField(
        queryset=Lab.objects.all(),
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(DeviceStatusChoices),
        required=False,
        widget=StaticSelect()
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )
    comments = CommentField(
        label='Comments'
    )

    model = Device
    fieldsets = (
        ('Device', ('device_role', 'status', 'tenant',)),
        ('Location', ('lab',)),
        ('Hardware', ('manufacturer', 'device_type',)),
    )
    nullable_fields = (
        'location', 'tenant', 'platform', 'description', 'comments',
    )
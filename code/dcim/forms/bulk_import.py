from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.forms.array import SimpleArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from dcim.choices import *
from dcim.models import *
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms import (
    CSVChoiceField, CSVContentTypeField, CSVModelChoiceField, CSVTypedChoiceField, SlugField, CSVModelMultipleChoiceField
)

__all__ = (
    'DeviceImportForm',
    'DeviceRoleImportForm',
    'DeviceTypeImportForm',
    'ManufacturerImportForm',
    'LabImportForm',
    'DepartmentImportForm',
)

class DepartmentImportForm(NetBoxModelImportForm):
    parent = CSVModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Name of parent Department')
    )

    class Meta:
        model = Department
        fields = ('name', 'slug', 'parent', 'description')

class LabImportForm(NetBoxModelImportForm):
    status = CSVChoiceField(
        choices=LabStatusChoices,
        help_text=_('Operational status')
    )
    group = CSVModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned group')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = Lab
        fields = (
            'name', 'slug', 'status', 'region', 'group', 'tenant', 'facility', 'time_zone', 'description',
            'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'tags'
        )
        help_texts = {
            'time_zone': mark_safe(
                _('Time zone (<a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">available options</a>)')
            )
        }

class ManufacturerImportForm(NetBoxModelImportForm):

    class Meta:
        model = Manufacturer
        fields = ('name', 'slug', 'description', 'tags')

class DeviceTypeImportForm(NetBoxModelImportForm):
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role', 'airflow',
            'description', 'comments',
        ]

class DeviceRoleImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = DeviceRole
        fields = ('name', 'slug', 'color', 'vm_role', 'description', 'tags')
        help_texts = {
            'color': mark_safe(_('RGB color in hexadecimal (e.g. <code>00ff00</code>)')),
        }

class BaseDeviceImportForm(NetBoxModelImportForm):
    device_role = CSVModelChoiceField(
        queryset=DeviceRole.objects.all(),
        to_field_name='name',
        help_text=_('Assigned role')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        help_text=_('Device type manufacturer')
    )
    device_type = CSVModelChoiceField(
        queryset=DeviceType.objects.all(),
        to_field_name='model',
        help_text=_('Device type model')
    )
    status = CSVChoiceField(
        choices=DeviceStatusChoices,
        help_text=_('Operational status')
    )

    class Meta:
        fields = []
        model = Device
        help_texts = {
            'vc_position': 'Virtual chassis position',
            'vc_priority': 'Virtual chassis priority',
        }

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit device type queryset by manufacturer
            params = {f"manufacturer__{self.fields['manufacturer'].to_field_name}": data.get('manufacturer')}
            self.fields['device_type'].queryset = self.fields['device_type'].queryset.filter(**params)

class DeviceImportForm(BaseDeviceImportForm):
    lab = CSVModelChoiceField(
        queryset=Lab.objects.all(),
        to_field_name='name',
        help_text=_('Assigned lab')
    )
    face = CSVChoiceField(
        choices=DeviceFaceChoices,
        required=False,
        help_text=_('Mounted rack face')
    )
    parent = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Parent device (for child devices)')
    )

    class Meta(BaseDeviceImportForm.Meta):
        fields = [
            'name', 'device_role', 'tenant', 'manufacturer', 'device_type', 'platform', 'serial', 'asset_tag', 'status',
            'lab', 'location', 'rack', 'position', 'face', 'parent', 'device_bay', 'virtual_chassis',
            'vc_position', 'vc_priority', 'cluster', 'description', 'comments', 'tags',
        ]

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:

            # Limit location queryset by assigned lab
            params = {f"lab__{self.fields['lab'].to_field_name}": data.get('lab')}
            self.fields['location'].queryset = self.fields['location'].queryset.filter(**params)
            self.fields['parent'].queryset = self.fields['parent'].queryset.filter(**params)

            # Limit rack queryset by assigned lab and location
            params = {
                f"lab__{self.fields['lab'].to_field_name}": data.get('lab'),
            }
            if 'location' in data:
                params.update({
                    f"location__{self.fields['location'].to_field_name}": data.get('location'),
                })
            self.fields['rack'].queryset = self.fields['rack'].queryset.filter(**params)

            # Limit device bay queryset by parent device
            if parent := data.get('parent'):
                params = {f"device__{self.fields['parent'].to_field_name}": parent}
                self.fields['device_bay'].queryset = self.fields['device_bay'].queryset.filter(**params)

    def clean(self):
        super().clean()

        # Inherit lab and rack from parent device
        if parent := self.cleaned_data.get('parent'):
            self.instance.lab = parent.lab
            self.instance.rack = parent.rack

        # Set parent_bay reverse relationship
        if device_bay := self.cleaned_data.get('device_bay'):
            self.instance.parent_bay = device_bay

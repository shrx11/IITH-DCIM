from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from timezone_field import TimeZoneFormField

from dcim.choices import *
from dcim.models import *
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms import (
    APISelect, add_blank_choice, BootstrapMixin, ClearableFileInput, CommentField, ContentTypeChoiceField,
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, JSONField, NumericArrayField, SelectWithPK, SmallTextarea,
    SlugField, StaticSelect, SelectSpeedWidget,
)

__all__ = (
    'DeviceForm',
    'DeviceRoleForm',
    'DeviceTypeForm',
    'ManufacturerForm',
    'LabForm',
    'DepartmentForm',
)

class DepartmentForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=Department.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        ('Department', (
            'parent','name', 'slug', #'description', 'tags',  
        )),
    )

    class Meta:
        model = Department
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class LabForm(TenancyForm, NetBoxModelForm):
    group = DynamicModelChoiceField(
        queryset=Department.objects.all(),
        required=False
    )
    slug = SlugField()
    time_zone = TimeZoneFormField(
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False,
        widget=StaticSelect()
    )
    # comments = CommentField()

    fieldsets = (
        ('Lab', (
            'name', 'slug', 'status', 'group', 'description', 
        )),        
    )

    class Meta:
        model = Lab
        fields = (
            'name', 'slug', 'status', 'region', 'group', 'tenant_group', 'tenant', 'description', 'tags',
        )
        widgets = {
            'physical_address': SmallTextarea(
                attrs={
                    'rows': 3,
                }
            ),
            'shipping_address': SmallTextarea(
                attrs={
                    'rows': 3,
                }
            ),
            'status': StaticSelect(),
            'time_zone': StaticSelect(),
        }
        help_texts = {
            'name': _("Full name of the lab"),
            'facility': _("Data center provider and facility (e.g. Equinix NY7)"),
            'time_zone': _("Local time zone"),
            'description': _("Short description (will appear in labs list)"),
            'physical_address': _("Physical location of the building (e.g. for GPS)"),
            'shipping_address': _("If different from the physical address"),
            'latitude': _("Latitude in decimal format (xx.yyyyyy)"),
            'longitude': _("Longitude in decimal format (xx.yyyyyy)")
        }


class ManufacturerForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('Manufacturer', (
            'name', 'slug', 'description', 'tags',
        )),
    )

    class Meta:
        model = Manufacturer
        fields = [
            'name', 'slug', 'description', 'tags',
        ]


class DeviceTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all()
    )
    slug = SlugField(
        slug_source='model'
    )
    # comments = CommentField()

    fieldsets = (
        ('Device Type', ('manufacturer', 'model', 'slug', 'tags')),
        ('Chassis', (
            'u_height', 'is_full_depth', 'part_number',
        )),
        # ('Images', ('front_image', 'rear_image')),
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role', 'airflow',
            'weight', 'weight_unit', 'front_image', 'rear_image', 'description', 'tags',
        ]


class DeviceRoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('Device Role', (
            'name', 'slug', 'color', 'vm_role', 'description', 'tags',
        )),
    )

    class Meta:
        model = DeviceRole
        fields = [
            'name', 'slug', 'color', 'vm_role', 'description', 'tags',
        ]


class DeviceForm(TenancyForm, NetBoxModelForm):
    lab_group = DynamicModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        initial_params={
            'labs': '$lab'
        }
    )
    lab = DynamicModelChoiceField(
        queryset=Lab.objects.all(),
        query_params={
            'region_id': '$region',
            'group_id': '$lab_group',
        }
    )
    position = forms.DecimalField(
        required=False,
        help_text=_("The lowest-numbered unit occupied by the device"),
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            attrs={
                'disabled-indicator': 'device',
                'data-dynamic-params': '[{"fieldName":"face","queryParam":"face"}]'
            }
        )
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': '$device_type'
        }
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all()
    )
    comments = CommentField()
    local_context_data = JSONField(
        required=False,
        label=''
    )

    class Meta:
        model = Device
        fields = [
            'name', 'device_role', 'device_type', 'serial', 'asset_tag', 'lab_group', 'lab', 'rack',#, 'tags', 'region','local_context_data'
            'location', 'position', 'face', 'status',
            'cluster_group', 'cluster', 'tenant_group', 'tenant',
            'description', 'comments',
        ]
        help_texts = {
            'device_role': _("The function this device serves"),
            'serial': _("Chassis serial number"),
            'local_context_data': _("Local config context data overwrites all source contexts in the final rendered "
                                    "config context"),
        }
        widgets = {
            'face': StaticSelect(),
            'status': StaticSelect(),
            'airflow': StaticSelect(),
            'primary_ip4': StaticSelect(),
            'primary_ip6': StaticSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]

                # Gather PKs of all interfaces belonging to this Device or a peer VirtualChassis member
                interface_ids = self.instance.vc_interfaces(if_master=False).values_list('pk', flat=True)

            # If editing an existing device, exclude it from the list of occupied rack units. This ensures that a device
            # can be flipped from one face to another.
            self.fields['position'].widget.add_query_param('exclude', self.instance.pk)

            # Disable rack assignment if this is a child device installed in a parent device
            if self.instance.device_type.is_child_device and hasattr(self.instance, 'parent_bay'):
                self.fields['lab'].disabled = True
                self.fields['rack'].disabled = True
                self.initial['lab'] = self.instance.parent_bay.device.lab_id
                self.initial['rack'] = self.instance.parent_bay.device.rack_id

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True

        # Rack position
        position = self.data.get('position') or self.initial.get('position')
        if position:
            self.fields['position'].widget.choices = [(position, f'U{position}')]


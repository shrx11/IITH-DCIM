import django_filters
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.db.models import Q
from extras.filtersets import LocalConfigContextFilterSet
from netbox.filtersets import (
    BaseFilterSet, ChangeLoggedModelFilterSet, OrganizationalModelFilterSet, NetBoxModelFilterSet,
)
from tenancy.filtersets import TenancyFilterSet, ContactModelFilterSet
from tenancy.models import *
from utilities.choices import ColorChoices
from utilities.filters import (
    ContentTypeFilter, MultiValueCharFilter, MultiValueMACAddressFilter, MultiValueNumberFilter, MultiValueWWNFilter,
    TreeNodeMultipleChoiceFilter,
)
from .choices import *
from .models import *

__all__ = (
    'DeviceFilterSet',
    'DeviceRoleFilterSet',
    'DeviceTypeFilterSet',
    'ManufacturerFilterSet',
    'LabFilterSet',
    'DepartmentFilterSet',
)

class DepartmentFilterSet(OrganizationalModelFilterSet, ContactModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Department.objects.all(),
        label=_('Parent department (ID)'),
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=Department.objects.all(),
        to_field_name='slug',
        label=_('Parent department (slug)'),
    )

    class Meta:
        model = Department
        fields = ['id', 'name', 'slug', 'description']


class LabFilterSet(NetBoxModelFilterSet, TenancyFilterSet, ContactModelFilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=LabStatusChoices,
        null_value=None
    )
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=Department.objects.all(),
        field_name='group',
        lookup_expr='in',
        label=_('Group (ID)'),
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=Department.objects.all(),
        lookup_expr='in',
        to_field_name='slug',
        label=_('Group (slug)'),
    )

    class Meta:
        model = Lab
        fields = (
            'id', 'name', 'slug', 'facility', 'latitude', 'longitude', 'description'
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(facility__icontains=value) |
            Q(description__icontains=value) |
            Q(physical_address__icontains=value) |
            Q(shipping_address__icontains=value) |
            Q(comments__icontains=value)
        )
        try:
            qs_filter |= Q(asns__asn=int(value.strip()))
        except ValueError:
            pass
        return queryset.filter(qs_filter).distinct()


class ManufacturerFilterSet(OrganizationalModelFilterSet, ContactModelFilterSet):

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'slug',]


class DeviceTypeFilterSet(NetBoxModelFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
   
    class Meta:
        model = DeviceType
        fields = [
            'id', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(manufacturer__name__icontains=value) |
            Q(model__icontains=value) |
            Q(part_number__icontains=value) |
            Q(comments__icontains=value)
        )


class DeviceRoleFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = DeviceRole
        fields = ['id', 'name', 'slug', 'color',]


class DeviceFilterSet(NetBoxModelFilterSet, TenancyFilterSet, ContactModelFilterSet, LocalConfigContextFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__manufacturer',
        queryset=Manufacturer.objects.all(),
        label=_('Manufacturer (ID)'),
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label=_('Manufacturer (slug)'),
    )
    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label=_('Device type (slug)'),
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        label=_('Device type (ID)'),
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_role_id',
        queryset=DeviceRole.objects.all(),
        label=_('Role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='device_role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    parent_device_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent_bay__device',
        queryset=Device.objects.all(),
        label=_('Parent Device (ID)'),
    )
    lab_group_id = TreeNodeMultipleChoiceFilter(
        queryset=Department.objects.all(),
        field_name='department',
        lookup_expr='in',
        label=_('Department (ID)'),
    )
    lab_group = TreeNodeMultipleChoiceFilter(
        queryset=Department.objects.all(),
        field_name='department',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Department (slug)'),
    )
    lab_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Lab.objects.all(),
        label=_('Lab (ID)'),
    )
    lab = django_filters.ModelMultipleChoiceFilter(
        field_name='lab__slug',
        queryset=Lab.objects.all(),
        to_field_name='slug',
        label=_('Lab name (slug)'),
    )
    model = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label=_('Device model (slug)'),
    )
    name = MultiValueCharFilter(
        lookup_expr='iexact'
    )
    status = django_filters.MultipleChoiceFilter(
        choices=DeviceStatusChoices,
        null_value=None
    )
    is_full_depth = django_filters.BooleanFilter(
        field_name='device_type__is_full_depth',
        label=_('Is full depth'),
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_address',
        label=_('MAC address'),
    )
    serial = MultiValueCharFilter(
        lookup_expr='iexact'
    )

    class Meta:
        model = Device
        fields = ['id', 'asset_tag', 'face', 'position',]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(inventoryitems__serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(comments__icontains=value) |
            Q(primary_ip4__address__startswith=value) |
            Q(primary_ip6__address__startswith=value)
        ).distinct()
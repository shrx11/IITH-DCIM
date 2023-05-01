from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Prefetch
from django.forms import ModelMultipleChoiceField, MultipleHiddenInput, modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.generic import View

from extras.views import ObjectConfigContextView
from netbox.views import generic
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator, get_paginate_count
from utilities.permissions import get_permission_for_model
from utilities.utils import count_related
from utilities.views import GetReturnURLMixin, ObjectPermissionRequiredMixin, ViewTab, register_model_view
from . import filtersets, forms, tables
from .choices import DeviceFaceChoices
from .models import *

#
# Departments
#

class DepartmentListView(generic.ObjectListView):
    queryset = Department.objects.add_related_count(
        Department.objects.all(),
        Lab,
        'group',
        'lab_count',
        cumulative=True
    )
    filterset = filtersets.DepartmentFilterSet
    filterset_form = forms.DepartmentFilterForm
    table = tables.DepartmentTable


@register_model_view(Department)
class DepartmentView(generic.ObjectView):
    queryset = Department.objects.all()

    def get_extra_context(self, request, instance):
        child_groups = Department.objects.add_related_count(
            Department.objects.all(),
            Lab,
            'group',
            'lab_count',
            cumulative=True
        ).restrict(request.user, 'view').filter(
            parent__in=instance.get_descendants(include_self=True)
        )
        child_groups_table = tables.DepartmentTable(child_groups)
        child_groups_table.columns.hide('actions')

        labs = Lab.objects.restrict(request.user, 'view').filter(
            group=instance
        )
        labs_table = tables.LabTable(labs, user=request.user, exclude=('group',))
        labs_table.configure(request)

        return {
            'child_groups_table': child_groups_table,
            'labs_table': labs_table,
        }


@register_model_view(Department, 'edit')
class DepartmentEditView(generic.ObjectEditView):
    queryset = Department.objects.all()
    form = forms.DepartmentForm


@register_model_view(Department, 'delete')
class DepartmentDeleteView(generic.ObjectDeleteView):
    queryset = Department.objects.all()


class DepartmentBulkImportView(generic.BulkImportView):
    queryset = Department.objects.all()
    model_form = forms.DepartmentImportForm
    table = tables.DepartmentTable


class DepartmentBulkEditView(generic.BulkEditView):
    queryset = Department.objects.add_related_count(
        Department.objects.all(),
        Lab,
        'group',
        'lab_count',
        cumulative=True
    )
    filterset = filtersets.DepartmentFilterSet
    table = tables.DepartmentTable
    form = forms.DepartmentBulkEditForm


class DepartmentBulkDeleteView(generic.BulkDeleteView):
    queryset = Department.objects.add_related_count(
        Department.objects.all(),
        Lab,
        'group',
        'lab_count',
        cumulative=True
    )
    filterset = filtersets.DepartmentFilterSet
    table = tables.DepartmentTable


#
# Labs
#

class LabListView(generic.ObjectListView):
    queryset = Lab.objects.all()
    filterset = filtersets.LabFilterSet
    filterset_form = forms.LabFilterForm
    table = tables.LabTable


@register_model_view(Lab)
class LabView(generic.ObjectView):
    queryset = Lab.objects.prefetch_related('tenant__group')

    def get_extra_context(self, request, instance):
        stats = {
            'device_count': Device.objects.restrict(request.user, 'view').filter(lab=instance).count(),
        }
        nonracked_devices = Device.objects.filter(
            lab=instance,
            rack__isnull=True,
            parent_bay__isnull=True
        ).prefetch_related('device_type__manufacturer', 'parent_bay', 'device_role')

        return {
            'stats': stats,
            'nonracked_devices': nonracked_devices.order_by('-pk')[:10],
            'total_nonracked_devices_count': nonracked_devices.count(),
        }


@register_model_view(Lab, 'edit')
class LabEditView(generic.ObjectEditView):
    queryset = Lab.objects.all()
    form = forms.LabForm


@register_model_view(Lab, 'delete')
class LabDeleteView(generic.ObjectDeleteView):
    queryset = Lab.objects.all()


class LabBulkImportView(generic.BulkImportView):
    queryset = Lab.objects.all()
    model_form = forms.LabImportForm
    table = tables.LabTable


class LabBulkEditView(generic.BulkEditView):
    queryset = Lab.objects.all()
    filterset = filtersets.LabFilterSet
    table = tables.LabTable
    form = forms.LabBulkEditForm


class LabBulkDeleteView(generic.BulkDeleteView):
    queryset = Lab.objects.all()
    filterset = filtersets.LabFilterSet
    table = tables.LabTable


#
# Manufacturers
#

class ManufacturerListView(generic.ObjectListView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer'),
    )
    filterset = filtersets.ManufacturerFilterSet
    filterset_form = forms.ManufacturerFilterForm
    table = tables.ManufacturerTable


@register_model_view(Manufacturer)
class ManufacturerView(generic.ObjectView):
    queryset = Manufacturer.objects.all()

    def get_extra_context(self, request, instance):
        device_types = DeviceType.objects.restrict(request.user, 'view').filter(
            manufacturer=instance
        ).annotate(
            instance_count=count_related(Device, 'device_type')
        )

        devicetypes_table = tables.DeviceTypeTable(device_types, user=request.user, exclude=('manufacturer',))
        devicetypes_table.configure(request)

        return {
            'devicetypes_table': devicetypes_table,
        }


@register_model_view(Manufacturer, 'edit')
class ManufacturerEditView(generic.ObjectEditView):
    queryset = Manufacturer.objects.all()
    form = forms.ManufacturerForm


@register_model_view(Manufacturer, 'delete')
class ManufacturerDeleteView(generic.ObjectDeleteView):
    queryset = Manufacturer.objects.all()


class ManufacturerBulkImportView(generic.BulkImportView):
    queryset = Manufacturer.objects.all()
    model_form = forms.ManufacturerImportForm
    table = tables.ManufacturerTable


class ManufacturerBulkEditView(generic.BulkEditView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer')
    )
    filterset = filtersets.ManufacturerFilterSet
    table = tables.ManufacturerTable
    form = forms.ManufacturerBulkEditForm


class ManufacturerBulkDeleteView(generic.BulkDeleteView):
    queryset = Manufacturer.objects.annotate(
        devicetype_count=count_related(DeviceType, 'manufacturer')
    )
    filterset = filtersets.ManufacturerFilterSet
    table = tables.ManufacturerTable


#
# Device types
#

class DeviceTypeListView(generic.ObjectListView):
    queryset = DeviceType.objects.annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    filterset_form = forms.DeviceTypeFilterForm
    table = tables.DeviceTypeTable


@register_model_view(DeviceType)
class DeviceTypeView(generic.ObjectView):
    queryset = DeviceType.objects.all()

    def get_extra_context(self, request, instance):
        instance_count = Device.objects.restrict(request.user).filter(device_type=instance).count()

        return {
            'instance_count': instance_count,
        }


@register_model_view(DeviceType, 'edit')
class DeviceTypeEditView(generic.ObjectEditView):
    queryset = DeviceType.objects.all()
    form = forms.DeviceTypeForm


@register_model_view(DeviceType, 'delete')
class DeviceTypeDeleteView(generic.ObjectDeleteView):
    queryset = DeviceType.objects.all()


class DeviceTypeImportView(generic.BulkImportView):
    additional_permissions = [
        'dcim.add_devicetype',
    ]
    queryset = DeviceType.objects.all()
    model_form = forms.DeviceTypeImportForm
    table = tables.DeviceTypeTable

    def prep_related_object_data(self, parent, data):
        data.update({'device_type': parent})
        return data


class DeviceTypeBulkEditView(generic.BulkEditView):
    queryset = DeviceType.objects.annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    table = tables.DeviceTypeTable
    form = forms.DeviceTypeBulkEditForm


class DeviceTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = DeviceType.objects.annotate(
        instance_count=count_related(Device, 'device_type')
    )
    filterset = filtersets.DeviceTypeFilterSet
    table = tables.DeviceTypeTable


#
# Device roles
#

class DeviceRoleListView(generic.ObjectListView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'device_role'),
    )
    filterset = filtersets.DeviceRoleFilterSet
    filterset_form = forms.DeviceRoleFilterForm
    table = tables.DeviceRoleTable


@register_model_view(DeviceRole)
class DeviceRoleView(generic.ObjectView):
    queryset = DeviceRole.objects.all()

    def get_extra_context(self, request, instance):
        devices = Device.objects.restrict(request.user, 'view').filter(
            device_role=instance
        )
        devices_table = tables.DeviceTable(devices, user=request.user, exclude=('device_role',))
        devices_table.configure(request)

        return {
            'devices_table': devices_table,
            'device_count': Device.objects.filter(device_role=instance).count(),
        }


@register_model_view(DeviceRole, 'devices', path='devices')
class DeviceRoleDevicesView(generic.ObjectChildrenView):
    queryset = DeviceRole.objects.all()
    child_model = Device
    table = tables.DeviceTable
    filterset = filtersets.DeviceFilterSet
    template_name = 'dcim/devicerole/devices.html'
    tab = ViewTab(
        label=_('Devices'),
        badge=lambda obj: obj.devices.count(),
        permission='dcim.view_device',
        weight=400
    )

    def get_children(self, request, parent):
        return Device.objects.restrict(request.user, 'view').filter(device_role=parent)

@register_model_view(DeviceRole, 'edit')
class DeviceRoleEditView(generic.ObjectEditView):
    queryset = DeviceRole.objects.all()
    form = forms.DeviceRoleForm


@register_model_view(DeviceRole, 'delete')
class DeviceRoleDeleteView(generic.ObjectDeleteView):
    queryset = DeviceRole.objects.all()


class DeviceRoleBulkImportView(generic.BulkImportView):
    queryset = DeviceRole.objects.all()
    model_form = forms.DeviceRoleImportForm
    table = tables.DeviceRoleTable


class DeviceRoleBulkEditView(generic.BulkEditView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'device_role'),
    )
    filterset = filtersets.DeviceRoleFilterSet
    table = tables.DeviceRoleTable
    form = forms.DeviceRoleBulkEditForm


class DeviceRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = DeviceRole.objects.annotate(
        device_count=count_related(Device, 'device_role'),
    )
    filterset = filtersets.DeviceRoleFilterSet
    table = tables.DeviceRoleTable


#
# Devices
#

class DeviceListView(generic.ObjectListView):
    queryset = Device.objects.all()
    filterset = filtersets.DeviceFilterSet
    filterset_form = forms.DeviceFilterForm
    table = tables.DeviceTable
    template_name = 'dcim/device_list.html'


@register_model_view(Device)
class DeviceView(generic.ObjectView):
    queryset = Device.objects.all()

    def get_extra_context(self, request, instance):
        # VirtualChassis members
        if instance.virtual_chassis is not None:
            vc_members = Device.objects.restrict(request.user, 'view').filter(
                virtual_chassis=instance.virtual_chassis
            ).order_by('vc_position')
        else:
            vc_members = []

        return {
            'vc_members': vc_members,
            'svg_extra': f'highlight=id:{instance.pk}'
        }


@register_model_view(Device, 'edit')
class DeviceEditView(generic.ObjectEditView):
    queryset = Device.objects.all()
    form = forms.DeviceForm
    template_name = 'dcim/device_edit.html'


@register_model_view(Device, 'delete')
class DeviceDeleteView(generic.ObjectDeleteView):
    queryset = Device.objects.all()

@register_model_view(Device, 'configcontext', path='config-context')
class DeviceConfigContextView(ObjectConfigContextView):
    queryset = Device.objects.annotate_config_context_data()
    base_template = 'dcim/device/base.html'


class DeviceBulkImportView(generic.BulkImportView):
    queryset = Device.objects.all()
    model_form = forms.DeviceImportForm
    table = tables.DeviceImportTable

    def save_object(self, object_form, request):
        obj = object_form.save()

        # For child devices, save the reverse relation to the parent device bay
        if getattr(obj, 'parent_bay', None):
            device_bay = obj.parent_bay
            device_bay.installed_device = obj
            device_bay.save()

        return obj


class DeviceBulkEditView(generic.BulkEditView):
    queryset = Device.objects.prefetch_related('device_type__manufacturer')
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable
    form = forms.DeviceBulkEditForm


class DeviceBulkDeleteView(generic.BulkDeleteView):
    queryset = Device.objects.prefetch_related('device_type__manufacturer')
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable


class DeviceBulkRenameView(generic.BulkRenameView):
    queryset = Device.objects.all()
    filterset = filtersets.DeviceFilterSet
    table = tables.DeviceTable


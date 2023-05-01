from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'dcim'
urlpatterns = [
    
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentEditView.as_view(), name='department_add'),
    path('departments/import/', views.DepartmentBulkImportView.as_view(), name='department_import'),
    path('departments/edit/', views.DepartmentBulkEditView.as_view(), name='department_bulk_edit'),
    path('departments/delete/', views.DepartmentBulkDeleteView.as_view(), name='department_bulk_delete'),
    path('departments/<int:pk>/', include(get_model_urls('dcim', 'department'))),

    # Labs
    path('labs/', views.LabListView.as_view(), name='lab_list'),
    path('labs/add/', views.LabEditView.as_view(), name='lab_add'),
    path('labs/import/', views.LabBulkImportView.as_view(), name='lab_import'),
    path('labs/edit/', views.LabBulkEditView.as_view(), name='lab_bulk_edit'),
    path('labs/delete/', views.LabBulkDeleteView.as_view(), name='lab_bulk_delete'),
    path('labs/<int:pk>/', include(get_model_urls('dcim', 'lab'))),

    # Manufacturers
    path('manufacturers/', views.ManufacturerListView.as_view(), name='manufacturer_list'),
    path('manufacturers/add/', views.ManufacturerEditView.as_view(), name='manufacturer_add'),
    path('manufacturers/import/', views.ManufacturerBulkImportView.as_view(), name='manufacturer_import'),
    path('manufacturers/edit/', views.ManufacturerBulkEditView.as_view(), name='manufacturer_bulk_edit'),
    path('manufacturers/delete/', views.ManufacturerBulkDeleteView.as_view(), name='manufacturer_bulk_delete'),
    path('manufacturers/<int:pk>/', include(get_model_urls('dcim', 'manufacturer'))),

    # Device types
    path('device-types/', views.DeviceTypeListView.as_view(), name='devicetype_list'),
    path('device-types/add/', views.DeviceTypeEditView.as_view(), name='devicetype_add'),
    path('device-types/import/', views.DeviceTypeImportView.as_view(), name='devicetype_import'),
    path('device-types/edit/', views.DeviceTypeBulkEditView.as_view(), name='devicetype_bulk_edit'),
    path('device-types/delete/', views.DeviceTypeBulkDeleteView.as_view(), name='devicetype_bulk_delete'),
    path('device-types/<int:pk>/', include(get_model_urls('dcim', 'devicetype'))),

    # Device roles
    path('device-roles/', views.DeviceRoleListView.as_view(), name='devicerole_list'),
    path('device-roles/add/', views.DeviceRoleEditView.as_view(), name='devicerole_add'),
    path('device-roles/import/', views.DeviceRoleBulkImportView.as_view(), name='devicerole_import'),
    path('device-roles/edit/', views.DeviceRoleBulkEditView.as_view(), name='devicerole_bulk_edit'),
    path('device-roles/delete/', views.DeviceRoleBulkDeleteView.as_view(), name='devicerole_bulk_delete'),
    path('device-roles/<int:pk>/', include(get_model_urls('dcim', 'devicerole'))),

    # Devices
    path('devices/', views.DeviceListView.as_view(), name='device_list'),
    path('devices/add/', views.DeviceEditView.as_view(), name='device_add'),
    path('devices/import/', views.DeviceBulkImportView.as_view(), name='device_import'),
    path('devices/edit/', views.DeviceBulkEditView.as_view(), name='device_bulk_edit'),
    path('devices/rename/', views.DeviceBulkRenameView.as_view(), name='device_bulk_rename'),
    path('devices/delete/', views.DeviceBulkDeleteView.as_view(), name='device_bulk_delete'),
    path('devices/<int:pk>/', include(get_model_urls('dcim', 'device'))),
    
]

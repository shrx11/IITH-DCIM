from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'tenancy'
urlpatterns = [

    # Tenant groups
    path('user-groups/', views.TenantGroupListView.as_view(), name='tenantgroup_list'),
    path('user-groups/add/', views.TenantGroupEditView.as_view(), name='tenantgroup_add'),
    path('user-groups/import/', views.TenantGroupBulkImportView.as_view(), name='tenantgroup_import'),
    path('user-groups/edit/', views.TenantGroupBulkEditView.as_view(), name='tenantgroup_bulk_edit'),
    path('user-groups/delete/', views.TenantGroupBulkDeleteView.as_view(), name='tenantgroup_bulk_delete'),
    path('user-groups/<int:pk>/', include(get_model_urls('tenancy', 'tenantgroup'))),

    # users
    path('users/', views.TenantListView.as_view(), name='tenant_list'),
    path('users/add/', views.TenantEditView.as_view(), name='tenant_add'),
    path('users/import/', views.TenantBulkImportView.as_view(), name='tenant_import'),
    path('users/edit/', views.TenantBulkEditView.as_view(), name='tenant_bulk_edit'),
    path('users/delete/', views.TenantBulkDeleteView.as_view(), name='tenant_bulk_delete'),
    path('users/<int:pk>/', include(get_model_urls('tenancy', 'tenant'))),

    # Contact groups
    path('contact-groups/', views.ContactGroupListView.as_view(), name='contactgroup_list'),
    path('contact-groups/add/', views.ContactGroupEditView.as_view(), name='contactgroup_add'),
    path('contact-groups/import/', views.ContactGroupBulkImportView.as_view(), name='contactgroup_import'),
    path('contact-groups/edit/', views.ContactGroupBulkEditView.as_view(), name='contactgroup_bulk_edit'),
    path('contact-groups/delete/', views.ContactGroupBulkDeleteView.as_view(), name='contactgroup_bulk_delete'),
    path('contact-groups/<int:pk>/', include(get_model_urls('tenancy', 'contactgroup'))),

    # Contact roles
    path('contact-roles/', views.ContactRoleListView.as_view(), name='contactrole_list'),
    path('contact-roles/add/', views.ContactRoleEditView.as_view(), name='contactrole_add'),
    path('contact-roles/import/', views.ContactRoleBulkImportView.as_view(), name='contactrole_import'),
    path('contact-roles/edit/', views.ContactRoleBulkEditView.as_view(), name='contactrole_bulk_edit'),
    path('contact-roles/delete/', views.ContactRoleBulkDeleteView.as_view(), name='contactrole_bulk_delete'),
    path('contact-roles/<int:pk>/', include(get_model_urls('tenancy', 'contactrole'))),

    # Contacts
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/add/', views.ContactEditView.as_view(), name='contact_add'),
    path('contacts/import/', views.ContactBulkImportView.as_view(), name='contact_import'),
    path('contacts/edit/', views.ContactBulkEditView.as_view(), name='contact_bulk_edit'),
    path('contacts/delete/', views.ContactBulkDeleteView.as_view(), name='contact_bulk_delete'),
    path('contacts/<int:pk>/', include(get_model_urls('tenancy', 'contact'))),

    # Contact assignments
    path('contact-assignments/add/', views.ContactAssignmentEditView.as_view(), name='contactassignment_add'),
    path('contact-assignments/<int:pk>/', include(get_model_urls('tenancy', 'contactassignment'))),

]

from netbox.api.routers import NetBoxRouter
from . import views


router = NetBoxRouter()
router.APIRootView = views.DCIMRootView

# Labs
router.register('regions', views.RegionViewSet)
router.register('lab-groups', views.DepartmentViewSet)
router.register('labs', views.LabViewSet)

# Device/module types
router.register('manufacturers', views.ManufacturerViewSet)
router.register('device-types', views.DeviceTypeViewSet)

# Device/modules
router.register('device-roles', views.DeviceRoleViewSet)
router.register('devices', views.DeviceViewSet)

app_name = 'dcim-api'
urlpatterns = router.urls

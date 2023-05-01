import graphene

from dcim import filtersets, models
from extras.graphql.mixins import ( ConfigContextMixin, ContactsMixin, ImageAttachmentsMixin, TagsMixin,
)
from netbox.graphql.scalars import BigInt
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, NetBoxObjectType

__all__ = (
    'DeviceType',
    'DeviceRoleType',
    'DeviceTypeType',
    'ManufacturerType',
    'LabType',
    'DepartmentType',
)

class DeviceType(ConfigContextMixin, ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):

    class Meta:
        model = models.Device
        fields = '__all__'
        filterset_class = filtersets.DeviceFilterSet

    def resolve_face(self, info):
        return self.face or None

    def resolve_airflow(self, info):
        return self.airflow or None

class DeviceRoleType(OrganizationalObjectType):

    class Meta:
        model = models.DeviceRole
        fields = '__all__'
        filterset_class = filtersets.DeviceRoleFilterSet

class DeviceTypeType(NetBoxObjectType):

    class Meta:
        model = models.DeviceType
        fields = '__all__'
        filterset_class = filtersets.DeviceTypeFilterSet

    def resolve_subdevice_role(self, info):
        return self.subdevice_role or None

    def resolve_airflow(self, info):
        return self.airflow or None

    def resolve_weight_unit(self, info):
        return self.weight_unit or None

class ManufacturerType(OrganizationalObjectType, ContactsMixin):

    class Meta:
        model = models.Manufacturer
        fields = '__all__'
        filterset_class = filtersets.ManufacturerFilterSet


class LabType(ImageAttachmentsMixin, ContactsMixin, NetBoxObjectType):
    asn = graphene.Field(BigInt)

    class Meta:
        model = models.Lab
        fields = '__all__'
        filterset_class = filtersets.LabFilterSet


class DepartmentType(ContactsMixin, OrganizationalObjectType):

    class Meta:
        model = models.Department
        fields = '__all__'
        filterset_class = filtersets.DepartmentFilterSet

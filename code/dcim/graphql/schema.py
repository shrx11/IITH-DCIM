import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class DCIMQuery(graphene.ObjectType):
    device = ObjectField(DeviceType)
    device_list = ObjectListField(DeviceType)

    device_role = ObjectField(DeviceRoleType)
    device_role_list = ObjectListField(DeviceRoleType)

    device_type = ObjectField(DeviceTypeType)
    device_type_list = ObjectListField(DeviceTypeType)

    manufacturer = ObjectField(ManufacturerType)
    manufacturer_list = ObjectListField(ManufacturerType)

    lab = ObjectField(LabType)
    lab_list = ObjectListField(LabType)

    lab_group = ObjectField(DepartmentType)
    lab_group_list = ObjectListField(DepartmentType)

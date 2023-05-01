from utilities.choices import ChoiceSet


#
# Labs
#

class LabStatusChoices(ChoiceSet):
    key = 'Lab.status'

    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_DECOMMISSIONING = 'decommissioning'
    STATUS_RETIRED = 'retired'

    CHOICES = [
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_STAGING, 'Staging', 'blue'),
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_DECOMMISSIONING, 'Decommissioning', 'yellow'),
        (STATUS_RETIRED, 'Retired', 'red'),
    ]


#
# DeviceTypes
#

class SubdeviceRoleChoices(ChoiceSet):

    ROLE_PARENT = 'parent'
    ROLE_CHILD = 'child'

    CHOICES = (
        (ROLE_PARENT, 'Parent'),
        (ROLE_CHILD, 'Child'),
    )


#
# Devices
#

class DeviceFaceChoices(ChoiceSet):

    FACE_FRONT = 'front'
    FACE_REAR = 'rear'

    CHOICES = (
        (FACE_FRONT, 'Front'),
        (FACE_REAR, 'Rear'),
    )


class DeviceStatusChoices(ChoiceSet):
    key = 'Device.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_INVENTORY = 'inventory'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = [
        (STATUS_OFFLINE, 'Offline', 'gray'),
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_STAGED, 'Staged', 'blue'),
        (STATUS_FAILED, 'Failed', 'red'),
        (STATUS_INVENTORY, 'Inventory', 'purple'),
        (STATUS_DECOMMISSIONING, 'Decommissioning', 'yellow'),
    ]
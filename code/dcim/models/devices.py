import decimal
import yaml

from functools import cached_property

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, F, ProtectedError
from django.db.models.functions import Lower
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from dcim.choices import *
from extras.models import ConfigContextModel
from extras.querysets import ConfigContextModelQuerySet
from netbox.config import ConfigItem
from netbox.models import OrganizationalModel, PrimaryModel
from utilities.choices import ColorChoices
from utilities.fields import ColorField, NaturalOrderingField


__all__ = (
    'Device',
    'DeviceRole',
    'DeviceType',
    'Manufacturer',
)


#
# Device Types
#

class Manufacturer(OrganizationalModel):
    """
    A Manufacturer represents a company which produces hardware devices; for example, Juniper or Dell.
    """
    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    def get_absolute_url(self):
        return reverse('dcim:manufacturer', args=[self.pk])


class DeviceType(PrimaryModel):
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='device_types'
    )
    model = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        max_length=100
    )
    part_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Discrete part number (optional)')
    )
    u_height = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        verbose_name='Height (U)'
    )
    is_full_depth = models.BooleanField(
        default=True,
        verbose_name='Is full depth',
        help_text=_('Device consumes both front and rear rack faces')
    )

    clone_fields = (
        'manufacturer', 'u_height', 'is_full_depth', 'subdevice_role',
    )
    prerequilab_models = (
        'dcim.Manufacturer',
    )

    class Meta:
        ordering = ['manufacturer', 'model']
        constraints = (
            models.UniqueConstraint(
                fields=('manufacturer', 'model'),
                name='%(app_label)s_%(class)s_unique_manufacturer_model'
            ),
            models.UniqueConstraint(
                fields=('manufacturer', 'slug'),
                name='%(app_label)s_%(class)s_unique_manufacturer_slug'
            ),
        )

    def __str__(self):
        return self.model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Save a copy of u_height for validation in clean()
        self._original_u_height = self.u_height

        # Save references to the original front/rear images
        self._original_front_image = self.front_image
        self._original_rear_image = self.rear_image

    def get_absolute_url(self):
        return reverse('dcim:devicetype', args=[self.pk])

    @property
    def get_full_name(self):
        return f"{ self.manufacturer } { self.model }"

    def to_yaml(self):
        data = {
            'manufacturer': self.manufacturer.name,
            'model': self.model,
            'slug': self.slug,
            'part_number': self.part_number,
            'u_height': float(self.u_height),
            'is_full_depth': self.is_full_depth,
        }

        return yaml.dump(dict(data), sort_keys=False)

    def clean(self):
        super().clean()

        # U height must be divisible by 0.5
        if self.u_height % decimal.Decimal(0.5):
            raise ValidationError({
                'u_height': "U height must be in increments of 0.5 rack units."
            })

        # If editing an existing DeviceType to have a larger u_height, first validate that *all* instances of it have
        # room to expand within their racks. This validation will impose a very high performance penalty when there are
        # many instances to check, but increasing the u_height of a DeviceType should be a very rare occurrence.
        if self.pk and self.u_height > self._original_u_height:
            for d in Device.objects.filter(device_type=self, position__isnull=False):
                face_required = None if self.is_full_depth else d.face
                u_available = d.rack.get_available_units(
                    u_height=self.u_height,
                    rack_face=face_required,
                    exclude=[d.pk]
                )
                if d.position not in u_available:
                    raise ValidationError({
                        'u_height': "Device {} in rack {} does not have sufficient space to accommodate a height of "
                                    "{}U".format(d, d.rack, self.u_height)
                    })

        # If modifying the height of an existing DeviceType to 0U, check for any instances assigned to a rack position.
        elif self.pk and self._original_u_height > 0 and self.u_height == 0:
            racked_instance_count = Device.objects.filter(
                device_type=self,
                position__isnull=False
            ).count()
            if racked_instance_count:
                url = f"{reverse('dcim:device_list')}?manufactuer_id={self.manufacturer_id}&device_type_id={self.pk}"
                raise ValidationError({
                    'u_height': mark_safe(
                        f'Unable to set 0U height: Found <a href="{url}">{racked_instance_count} instances</a> already '
                        f'mounted within racks.'
                    )
                })

        if (
                self.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT
        ) and self.pk and self.devicebaytemplates.count():
            raise ValidationError({
                'subdevice_role': "Must delete all device bay templates associated with this device before "
                                  "declassifying it as a parent device."
            })

        if self.u_height and self.subdevice_role == SubdeviceRoleChoices.ROLE_CHILD:
            raise ValidationError({
                'u_height': "Child device types must be 0U."
            })

    def save(self, *args, **kwargs):
        ret = super().save(*args, **kwargs)

        # Delete any previously uploaded image files that are no longer in use
        if self.front_image != self._original_front_image:
            self._original_front_image.delete(save=False)
        if self.rear_image != self._original_rear_image:
            self._original_rear_image.delete(save=False)

        return ret

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        # Delete any uploaded image files
        if self.front_image:
            self.front_image.delete(save=False)
        if self.rear_image:
            self.rear_image.delete(save=False)

    @property
    def is_parent_device(self):
        return self.subdevice_role == SubdeviceRoleChoices.ROLE_PARENT

    @property
    def is_child_device(self):
        return self.subdevice_role == SubdeviceRoleChoices.ROLE_CHILD

#
# Devices
#

class DeviceRole(OrganizationalModel):
    """
    Devices are organized by functional role; for example, "Core Switch" or "File Server". Each DeviceRole is assigned a
    color to be used when displaying rack elevations. The vm_role field determines whether the role is applicable to
    virtual machines as well.
    """
    color = ColorField(
        default=ColorChoices.COLOR_GREY
    )
    vm_role = models.BooleanField(
        default=True,
        verbose_name='VM Role',
        help_text=_('Virtual machines may be assigned to this role')
    )

    def get_absolute_url(self):
        return reverse('dcim:devicerole', args=[self.pk])


class Device(PrimaryModel, ConfigContextModel):
    """
    A Device represents a piece of physical hardware mounted within a Rack. Each Device is assigned a DeviceType,
    DeviceRole, and (optionally) a Platform. Device names are not required, however if one is set it must be unique.

    Each Device must be assigned to a lab, and optionally to a rack within that lab. Associating a device with a
    particular rack face or unit is optional (for example, vertically mounted PDUs do not consume rack units).

    When a new Device is created, console/power/interface/device bay components are created along with it as dictated
    by the component templates assigned to its DeviceType. Components can also be added, modified, or deleted after the
    creation of a Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.PROTECT,
        related_name='instances'
    )
    device_role = models.ForeignKey(
        to='dcim.DeviceRole',
        on_delete=models.PROTECT,
        related_name='devices'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True,
        null=True
    )
    serial = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Serial number'
    )
    asset_tag = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Asset tag',
        help_text=_('A unique tag used to identify this device')
    )
    lab = models.ForeignKey(
        to='dcim.Lab',
        on_delete=models.PROTECT,
        related_name='devices'
    )
    location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True
    )
    rack = models.ForeignKey(
        to='dcim.Rack',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True
    )
    position = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(99.5)],
        verbose_name='Position (U)',
        help_text=_('The lowest-numbered unit occupied by the device')
    )
    face = models.CharField(
        max_length=50,
        blank=True,
        choices=DeviceFaceChoices,
        verbose_name='Rack face'
    )
    status = models.CharField(
        max_length=50,
        choices=DeviceStatusChoices,
        default=DeviceStatusChoices.STATUS_ACTIVE
    )

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    
    objects = ConfigContextModelQuerySet.as_manager()

    clone_fields = (
        'device_type', 'device_role', 'tenant', 'lab', 'rack', 'face', 'status',
        
    )
    prerequilab_models = (
        'dcim.Lab',
        'dcim.DeviceRole',
        'dcim.DeviceType',
    )

    class Meta:
        ordering = ('_name', 'pk')  # Name may be null
        constraints = (
            models.UniqueConstraint(
                Lower('name'), 'lab', 'tenant',
                name='%(app_label)s_%(class)s_unique_name_lab_tenant'
            ),
            models.UniqueConstraint(
                Lower('name'), 'lab',
                name='%(app_label)s_%(class)s_unique_name_lab',
                condition=Q(tenant__isnull=True),
                violation_error_message="Device name must be unique per lab."
            ),
            models.UniqueConstraint(
                fields=('rack', 'position', 'face'),
                name='%(app_label)s_%(class)s_unique_rack_position_face'
            ),
            models.UniqueConstraint(
                fields=('virtual_chassis', 'vc_position'),
                name='%(app_label)s_%(class)s_unique_virtual_chassis_vc_position'
            ),
        )

    def __str__(self):
        if self.name and self.asset_tag:
            return f'{self.name} ({self.asset_tag})'
        elif self.name:
            return self.name
        elif self.virtual_chassis and self.asset_tag:
            return f'{self.virtual_chassis.name}:{self.vc_position} ({self.asset_tag})'
        elif self.virtual_chassis:
            return f'{self.virtual_chassis.name}:{self.vc_position} ({self.pk})'
        elif self.device_type and self.asset_tag:
            return f'{self.device_type.manufacturer} {self.device_type.model} ({self.asset_tag})'
        elif self.device_type:
            return f'{self.device_type.manufacturer} {self.device_type.model} ({self.pk})'
        return super().__str__()

    def get_absolute_url(self):
        return reverse('dcim:device', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate lab/location/rack combination
        if self.rack and self.lab != self.rack.lab:
            raise ValidationError({
                'rack': f"Rack {self.rack} does not belong to lab {self.lab}.",
            })
        if self.location and self.lab != self.location.lab:
            raise ValidationError({
                'location': f"Location {self.location} does not belong to lab {self.lab}.",
            })
        if self.rack and self.location and self.rack.location != self.location:
            raise ValidationError({
                'rack': f"Rack {self.rack} does not belong to location {self.location}.",
            })

        if self.rack is None:
            if self.face:
                raise ValidationError({
                    'face': "Cannot select a rack face without assigning a rack.",
                })
            if self.position:
                raise ValidationError({
                    'position': "Cannot select a rack position without assigning a rack.",
                })

        # Validate rack position and face
        if self.position and self.position % decimal.Decimal(0.5):
            raise ValidationError({
                'position': "Position must be in increments of 0.5 rack units."
            })
        if self.position and not self.face:
            raise ValidationError({
                'face': "Must specify rack face when defining rack position.",
            })

        # Prevent 0U devices from being assigned to a specific position
        if hasattr(self, 'device_type'):
            if self.position and self.device_type.u_height == 0:
                raise ValidationError({
                    'position': f"A U0 device type ({self.device_type}) cannot be assigned to a rack position."
                })

        if self.rack:

            try:
                # Child devices cannot be assigned to a rack face/unit
                if self.device_type.is_child_device and self.face:
                    raise ValidationError({
                        'face': "Child device types cannot be assigned to a rack face. This is an attribute of the "
                                "parent device."
                    })
                if self.device_type.is_child_device and self.position:
                    raise ValidationError({
                        'position': "Child device types cannot be assigned to a rack position. This is an attribute of "
                                    "the parent device."
                    })

                # Validate rack space
                rack_face = self.face if not self.device_type.is_full_depth else None
                exclude_list = [self.pk] if self.pk else []
                available_units = self.rack.get_available_units(
                    u_height=self.device_type.u_height, rack_face=rack_face, exclude=exclude_list
                )
                if self.position and self.position not in available_units:
                    raise ValidationError({
                        'position': f"U{self.position} is already occupied or does not have sufficient space to "
                                    f"accommodate this device type: {self.device_type} ({self.device_type.u_height}U)"
                    })

            except DeviceType.DoesNotExist:
                pass

        # Validate primary IP addresses
        vc_interfaces = self.vc_interfaces(if_master=False)
        if self.primary_ip4:
            if self.primary_ip4.family != 4:
                raise ValidationError({
                    'primary_ip4': f"{self.primary_ip4} is not an IPv4 address."
                })
            if self.primary_ip4.assigned_object in vc_interfaces:
                pass
            elif self.primary_ip4.nat_inside is not None and self.primary_ip4.nat_inside.assigned_object in vc_interfaces:
                pass
            else:
                raise ValidationError({
                    'primary_ip4': f"The specified IP address ({self.primary_ip4}) is not assigned to this device."
                })
        if self.primary_ip6:
            if self.primary_ip6.family != 6:
                raise ValidationError({
                    'primary_ip6': f"{self.primary_ip6} is not an IPv6 address."
                })
            if self.primary_ip6.assigned_object in vc_interfaces:
                pass
            elif self.primary_ip6.nat_inside is not None and self.primary_ip6.nat_inside.assigned_object in vc_interfaces:
                pass
            else:
                raise ValidationError({
                    'primary_ip6': f"The specified IP address ({self.primary_ip6}) is not assigned to this device."
                })

        # Validate manufacturer/platform
        if hasattr(self, 'device_type') and self.platform:
            if self.platform.manufacturer and self.platform.manufacturer != self.device_type.manufacturer:
                raise ValidationError({
                    'platform': f"The assigned platform is limited to {self.platform.manufacturer} device types, but "
                                f"this device's type belongs to {self.device_type.manufacturer}."
                })

        # A Device can only be assigned to a Cluster in the same Lab (or no Lab)
        if self.cluster and self.cluster.lab is not None and self.cluster.lab != self.lab:
            raise ValidationError({
                'cluster': "The assigned cluster belongs to a different lab ({})".format(self.cluster.lab)
            })

        # Validate virtual chassis assignment
        if self.virtual_chassis and self.vc_position is None:
            raise ValidationError({
                'vc_position': "A device assigned to a virtual chassis must have its position defined."
            })

    def _instantiate_components(self, queryset, bulk_create=True):
        """
        Instantiate components for the device from the specified component templates.

        Args:
            bulk_create: If True, bulk_create() will be called to create all components in a single query
                         (default). Otherwise, save() will be called on each instance individually.
        """
        if bulk_create:
            components = [obj.instantiate(device=self) for obj in queryset]
            if not components:
                return
            model = components[0]._meta.model
            model.objects.bulk_create(components)
            # Manually send the post_save signal for each of the newly created components
            for component in components:
                post_save.send(
                    sender=model,
                    instance=component,
                    created=True,
                    raw=False,
                    using='default',
                    update_fields=None
                )
        else:
            for obj in queryset:
                component = obj.instantiate(device=self)
                component.save()

    def save(self, *args, **kwargs):
        is_new = not bool(self.pk)

        # Inherit airflow attribute from DeviceType if not set
        if is_new and not self.airflow:
            self.airflow = self.device_type.airflow

        if self.rack and self.rack.location:
            self.location = self.rack.location

        super().save(*args, **kwargs)

        # If this is a new Device, instantiate all the related components per the DeviceType definition
        if is_new:
            self._instantiate_components(self.device_type.consoleporttemplates.all())
            self._instantiate_components(self.device_type.consoleserverporttemplates.all())
            self._instantiate_components(self.device_type.powerporttemplates.all())
            self._instantiate_components(self.device_type.poweroutlettemplates.all())
            self._instantiate_components(self.device_type.interfacetemplates.all())
            self._instantiate_components(self.device_type.rearporttemplates.all())
            self._instantiate_components(self.device_type.frontporttemplates.all())
            self._instantiate_components(self.device_type.modulebaytemplates.all())
            self._instantiate_components(self.device_type.devicebaytemplates.all())
            # Disable bulk_create to accommodate MPTT
            self._instantiate_components(self.device_type.inventoryitemtemplates.all(), bulk_create=False)

        # Update Lab and Rack assignment for any child Devices
        devices = Device.objects.filter(parent_bay__device=self)
        for device in devices:
            device.lab = self.lab
            device.rack = self.rack
            device.location = self.location
            device.save()

    @property
    def identifier(self):
        """
        Return the device name if set; otherwise return the Device's primary key as {pk}
        """
        if self.name is not None:
            return self.name
        return '{{{}}}'.format(self.pk)

    @property
    def primary_ip(self):
        if ConfigItem('PREFER_IPV4')() and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None

    @property
    def interfaces_count(self):
        return self.vc_interfaces().count()

    def get_vc_master(self):
        """
        If this Device is a VirtualChassis member, return the VC master. Otherwise, return None.
        """
        return self.virtual_chassis.master if self.virtual_chassis else None


    def get_children(self):
        """
        Return the set of child Devices installed in DeviceBays within this Device.
        """
        return Device.objects.filter(parent_bay__device=self.pk)

    def get_status_color(self):
        return DeviceStatusChoices.colors.get(self.status)
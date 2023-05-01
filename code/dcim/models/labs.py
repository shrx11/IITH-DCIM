from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext as _
from timezone_field import TimeZoneField

from dcim.choices import *
from netbox.models import NestedGroupModel, PrimaryModel
from utilities.fields import NaturalOrderingField

__all__ = (
    'Lab',
    'Department',
)

#
# Departments
#

class Department(NestedGroupModel):
    """
    A department is an arbitrary grouping of labs. For example, you might have corporate labs and customer labs; and
    within corporate labs you might distinguish between offices and data centers. Like regions, departments can be
    nested recursively to form a hierarchy.
    """
    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    class Meta:
        verbose_name = "Department"
        constraints = (
            models.UniqueConstraint(
                fields=('parent', 'name'),
                name='%(app_label)s_%(class)s_parent_name'
            ),
            models.UniqueConstraint(
                fields=('name',),
                name='%(app_label)s_%(class)s_name',
                condition=Q(parent__isnull=True),
                violation_error_message="A top-level department with this name already exists."
            ),
            models.UniqueConstraint(
                fields=('parent', 'slug'),
                name='%(app_label)s_%(class)s_parent_slug'
            ),
            models.UniqueConstraint(
                fields=('slug',),
                name='%(app_label)s_%(class)s_slug',
                condition=Q(parent__isnull=True),
                violation_error_message="A top-level department with this slug already exists."
            ),
        )

    def get_absolute_url(self):
        return reverse('dcim:department', args=[self.pk])

    def get_lab_count(self):
        return Lab.objects.filter(
            Q(group=self) |
            Q(group__in=self.get_descendants())
        ).count()


#
# Labs
#

class Lab(PrimaryModel):
    """
    A Lab represents a geographic location within a network; typically a building or campus. The optional facility
    field can be used to include an external designation, such as a data center name (e.g. Equinix SV6).
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    status = models.CharField(
        max_length=50,
        choices=LabStatusChoices,
        default=LabStatusChoices.STATUS_ACTIVE
    )
    region = models.ForeignKey(
        to='dcim.Region',
        on_delete=models.SET_NULL,
        related_name='labs',
        blank=True,
        null=True
    )
    group = models.ForeignKey(
        to='dcim.Department',
        on_delete=models.SET_NULL,
        related_name='labs',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='labs',
        blank=True,
        null=True
    )
    facility = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Local facility ID or description')
    )
    time_zone = TimeZoneField(
        blank=True
    )
    physical_address = models.CharField(
        max_length=200,
        blank=True
    )
    shipping_address = models.CharField(
        max_length=200,
        blank=True
    )
    latitude = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_('GPS coordinate (latitude)')
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_('GPS coordinate (longitude)')
    )

    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    clone_fields = (
        'status', 'region', 'group', 'tenant', 'facility', 'time_zone', 'physical_address', 'shipping_address',
        'latitude', 'longitude', 'description',
    )

    class Meta:
        verbose_name = "Lab"
        ordering = ('_name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:lab', args=[self.pk])

    def get_status_color(self):
        return LabStatusChoices.colors.get(self.status)

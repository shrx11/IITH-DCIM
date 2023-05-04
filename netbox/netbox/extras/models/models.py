import json
import urllib.parse

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.validators import ValidationError
from django.db import models
from django.http import HttpResponse, QueryDict
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _
from rest_framework.utils.encoders import JSONEncoder

from extras.choices import *
from extras.conditions import ConditionSet
from extras.constants import *
from extras.utils import FeatureQuery, image_upload
from netbox.config import get_config
from netbox.models import ChangeLoggedModel
from netbox.models.features import (
    CloningMixin, CustomFieldsMixin, CustomLinksMixin, ExportTemplatesMixin, SyncedDataMixin, TagsMixin,
)
from utilities.querysets import RestrictedQuerySet
from utilities.utils import clean_html, render_jinja2

__all__ = (
    'ConfigRevision',
    'CustomLink',
    'ExportTemplate',
    'ImageAttachment',
    'JournalEntry',
    'SavedFilter',
    'Webhook',
)


class Webhook(ExportTemplatesMixin, ChangeLoggedModel):
    """
    A Webhook defines a request that will be sent to a remote application when an object is created, updated, and/or
    delete in NetBox. The request will contain a representation of the object, which the remote application can act on.
    Each Webhook can be limited to firing only on certain actions or certain object types.
    """
    content_types = models.ManyToManyField(
        to=ContentType,
        related_name='webhooks',
        verbose_name='Object types',
        limit_choices_to=FeatureQuery('webhooks'),
        help_text=_("The object(s) to which this Webhook applies.")
    )
    name = models.CharField(
        max_length=150,
        unique=True
    )
    type_create = models.BooleanField(
        default=False,
        help_text=_("Triggers when a matching object is created.")
    )
    type_update = models.BooleanField(
        default=False,
        help_text=_("Triggers when a matching object is updated.")
    )
    type_delete = models.BooleanField(
        default=False,
        help_text=_("Triggers when a matching object is deleted.")
    )
    type_job_start = models.BooleanField(
        default=False,
        help_text=_("Triggers when a job for a matching object is started.")
    )
    type_job_end = models.BooleanField(
        default=False,
        help_text=_("Triggers when a job for a matching object terminates.")
    )
    payload_url = models.CharField(
        max_length=500,
        verbose_name='URL',
        help_text=_('This URL will be called using the HTTP method defined when the webhook is called. '
                    'Jinja2 template processing is supported with the same context as the request body.')
    )
    enabled = models.BooleanField(
        default=True
    )
    http_method = models.CharField(
        max_length=30,
        choices=WebhookHttpMethodChoices,
        default=WebhookHttpMethodChoices.METHOD_POST,
        verbose_name='HTTP method'
    )
    http_content_type = models.CharField(
        max_length=100,
        default=HTTP_CONTENT_TYPE_JSON,
        verbose_name='HTTP content type',
        help_text=_('The complete list of official content types is available '
                    '<a href="https://www.iana.org/assignments/media-types/media-types.xhtml">here</a>.')
    )
    additional_headers = models.TextField(
        blank=True,
        help_text=_("User-supplied HTTP headers to be sent with the request in addition to the HTTP content type. "
                    "Headers should be defined in the format <code>Name: Value</code>. Jinja2 template processing is "
                    "supported with the same context as the request body (below).")
    )
    body_template = models.TextField(
        blank=True,
        help_text=_('Jinja2 template for a custom request body. If blank, a JSON object representing the change will be '
                    'included. Available context data includes: <code>event</code>, <code>model</code>, '
                    '<code>timestamp</code>, <code>username</code>, <code>request_id</code>, and <code>data</code>.')
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("When provided, the request will include a 'X-Hook-Signature' "
                    "header containing a HMAC hex digest of the payload body using "
                    "the secret as the key. The secret is not transmitted in "
                    "the request.")
    )
    conditions = models.JSONField(
        blank=True,
        null=True,
        help_text=_("A set of conditions which determine whether the webhook will be generated.")
    )
    ssl_verification = models.BooleanField(
        default=True,
        verbose_name='SSL verification',
        help_text=_("Enable SSL certificate verification. Disable with caution!")
    )
    ca_file_path = models.CharField(
        max_length=4096,
        null=True,
        blank=True,
        verbose_name='CA File Path',
        help_text=_('The specific CA certificate file to use for SSL verification. '
                    'Leave blank to use the system defaults.')
    )

    class Meta:
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('payload_url', 'type_create', 'type_update', 'type_delete'),
                name='%(app_label)s_%(class)s_unique_payload_url_types'
            ),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:webhook', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/webhook/'

    def clean(self):
        super().clean()

        # At least one action type must be selected
        if not any([
            self.type_create, self.type_update, self.type_delete, self.type_job_start, self.type_job_end
        ]):
            raise ValidationError(
                "At least one event type must be selected: create, update, delete, job_start, and/or job_end."
            )

        if self.conditions:
            try:
                ConditionSet(self.conditions)
            except ValueError as e:
                raise ValidationError({'conditions': e})

        # CA file path requires SSL verification enabled
        if not self.ssl_verification and self.ca_file_path:
            raise ValidationError({
                'ca_file_path': 'Do not specify a CA certificate file if SSL verification is disabled.'
            })

    def render_headers(self, context):
        """
        Render additional_headers and return a dict of Header: Value pairs.
        """
        if not self.additional_headers:
            return {}
        ret = {}
        data = render_jinja2(self.additional_headers, context)
        for line in data.splitlines():
            header, value = line.split(':', 1)
            ret[header.strip()] = value.strip()
        return ret

    def render_body(self, context):
        """
        Render the body template, if defined. Otherwise, jump the context as a JSON object.
        """
        if self.body_template:
            return render_jinja2(self.body_template, context)
        else:
            return json.dumps(context, cls=JSONEncoder)

    def render_payload_url(self, context):
        """
        Render the payload URL.
        """
        return render_jinja2(self.payload_url, context)


class CustomLink(CloningMixin, ExportTemplatesMixin, ChangeLoggedModel):
    """
    A custom link to an external representation of a NetBox object. The link text and URL fields accept Jinja2 template
    code to be rendered with an object as context.
    """
    content_types = models.ManyToManyField(
        to=ContentType,
        related_name='custom_links',
        help_text=_('The object type(s) to which this link applies.')
    )
    name = models.CharField(
        max_length=100,
        unique=True
    )
    enabled = models.BooleanField(
        default=True
    )
    link_text = models.TextField(
        help_text=_("Jinja2 template code for link text")
    )
    link_url = models.TextField(
        verbose_name='Link URL',
        help_text=_("Jinja2 template code for link URL")
    )
    weight = models.PositiveSmallIntegerField(
        default=100
    )
    group_name = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Links with the same group will appear as a dropdown menu")
    )
    button_class = models.CharField(
        max_length=30,
        choices=CustomLinkButtonClassChoices,
        default=CustomLinkButtonClassChoices.DEFAULT,
        help_text=_("The class of the first link in a group will be used for the dropdown button")
    )
    new_window = models.BooleanField(
        default=False,
        help_text=_("Force link to open in a new window")
    )

    clone_fields = (
        'content_types', 'enabled', 'weight', 'group_name', 'button_class', 'new_window',
    )

    class Meta:
        ordering = ['group_name', 'weight', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:customlink', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/customlink/'

    def render(self, context):
        """
        Render the CustomLink given the provided context, and return the text, link, and link_target.

        :param context: The context passed to Jinja2
        """
        text = render_jinja2(self.link_text, context)
        if not text:
            return {}
        link = render_jinja2(self.link_url, context)
        link_target = ' target="_blank"' if self.new_window else ''

        # Sanitize link text
        allowed_schemes = get_config().ALLOWED_URL_SCHEMES
        text = clean_html(text, allowed_schemes)

        # Sanitize link
        link = urllib.parse.quote_plus(link, safe='/:?&=%+[]@#')

        # Verify link scheme is allowed
        result = urllib.parse.urlparse(link)
        if result.scheme and result.scheme not in allowed_schemes:
            link = ""

        return {
            'text': text,
            'link': link,
            'link_target': link_target,
        }


class ExportTemplate(SyncedDataMixin, CloningMixin, ExportTemplatesMixin, ChangeLoggedModel):
    content_types = models.ManyToManyField(
        to=ContentType,
        related_name='export_templates',
        help_text=_('The object type(s) to which this template applies.')
    )
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    template_code = models.TextField(
        help_text=_('Jinja2 template code. The list of objects being exported is passed as a context variable named '
                    '<code>queryset</code>.')
    )
    mime_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='MIME type',
        help_text=_('Defaults to <code>text/plain; charset=utf-8</code>')
    )
    file_extension = models.CharField(
        max_length=15,
        blank=True,
        help_text=_('Extension to append to the rendered filename')
    )
    as_attachment = models.BooleanField(
        default=True,
        help_text=_("Download file as attachment")
    )

    clone_fields = (
        'content_types', 'template_code', 'mime_type', 'file_extension', 'as_attachment',
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:exporttemplate', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/exporttemplate/'

    def clean(self):
        super().clean()

        if self.name.lower() == 'table':
            raise ValidationError({
                'name': f'"{self.name}" is a reserved name. Please choose a different name.'
            })

    def sync_data(self):
        """
        Synchronize template content from the designated DataFile (if any).
        """
        self.template_code = self.data_file.data_as_string

    def render(self, queryset):
        """
        Render the contents of the template.
        """
        context = {
            'queryset': queryset
        }
        output = render_jinja2(self.template_code, context)

        # Replace CRLF-style line terminators
        output = output.replace('\r\n', '\n')

        return output

    def render_to_response(self, queryset):
        """
        Render the template to an HTTP response, delivered as a named file attachment
        """
        output = self.render(queryset)
        mime_type = 'text/plain; charset=utf-8' if not self.mime_type else self.mime_type

        # Build the response
        response = HttpResponse(output, content_type=mime_type)

        if self.as_attachment:
            basename = queryset.model._meta.verbose_name_plural.replace(' ', '_')
            extension = f'.{self.file_extension}' if self.file_extension else ''
            filename = f'netbox_{basename}{extension}'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response


class SavedFilter(CloningMixin, ExportTemplatesMixin, ChangeLoggedModel):
    """
    A set of predefined keyword parameters that can be reused to filter for specific objects.
    """
    content_types = models.ManyToManyField(
        to=ContentType,
        related_name='saved_filters',
        help_text=_('The object type(s) to which this filter applies.')
    )
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    weight = models.PositiveSmallIntegerField(
        default=100
    )
    enabled = models.BooleanField(
        default=True
    )
    shared = models.BooleanField(
        default=True
    )
    parameters = models.JSONField()

    clone_fields = (
        'content_types', 'weight', 'enabled', 'parameters',
    )

    class Meta:
        ordering = ('weight', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:savedfilter', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/savedfilter/'

    def clean(self):
        super().clean()

        # Verify that `parameters` is a JSON object
        if type(self.parameters) is not dict:
            raise ValidationError(
                {'parameters': 'Filter parameters must be stored as a dictionary of keyword arguments.'}
            )

    @property
    def url_params(self):
        qd = QueryDict(mutable=True)
        qd.update(self.parameters)
        return qd.urlencode()


class ImageAttachment(ChangeLoggedModel):
    """
    An uploaded image which is associated with an object.
    """
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    parent = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    image = models.ImageField(
        upload_to=image_upload,
        height_field='image_height',
        width_field='image_width'
    )
    image_height = models.PositiveSmallIntegerField()
    image_width = models.PositiveSmallIntegerField()
    name = models.CharField(
        max_length=50,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = ('content_type', 'object_id')

    class Meta:
        ordering = ('name', 'pk')  # name may be non-unique

    def __str__(self):
        if self.name:
            return self.name
        filename = self.image.name.rsplit('/', 1)[-1]
        return filename.split('_', 2)[2]

    def delete(self, *args, **kwargs):

        _name = self.image.name

        super().delete(*args, **kwargs)

        # Delete file from disk
        self.image.delete(save=False)

        # Deleting the file erases its name. We restore the image's filename here in case we still need to reference it
        # before the request finishes. (For example, to display a message indicating the ImageAttachment was deleted.)
        self.image.name = _name

    @property
    def size(self):
        """
        Wrapper around `image.size` to suppress an OSError in case the file is inaccessible. Also opportunistically
        catch other exceptions that we know other storage back-ends to throw.
        """
        expected_exceptions = [OSError]

        try:
            from botocore.exceptions import ClientError
            expected_exceptions.append(ClientError)
        except ImportError:
            pass

        try:
            return self.image.size
        except tuple(expected_exceptions):
            return None

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.parent
        return objectchange


class JournalEntry(CustomFieldsMixin, CustomLinksMixin, TagsMixin, ExportTemplatesMixin, ChangeLoggedModel):
    """
    A historical remark concerning an object; collectively, these form an object's journal. The journal is used to
    preserve historical context around an object, and complements NetBox's built-in change logging. For example, you
    might record a new journal entry when a device undergoes maintenance, or when a prefix is expanded.
    """
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id'
    )
    created_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    kind = models.CharField(
        max_length=30,
        choices=JournalEntryKindChoices,
        default=JournalEntryKindChoices.KIND_INFO
    )
    comments = models.TextField()

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'journal entries'

    def __str__(self):
        created = timezone.localtime(self.created)
        return f"{date_format(created, format='SHORT_DATETIME_FORMAT')} ({self.get_kind_display()})"

    def get_absolute_url(self):
        return reverse('extras:journalentry', args=[self.pk])

    def clean(self):
        super().clean()

        # Prevent the creation of journal entries on unsupported models
        permitted_types = ContentType.objects.filter(FeatureQuery('journaling').get_query())
        if self.assigned_object_type not in permitted_types:
            raise ValidationError(f"Journaling is not supported for this object type ({self.assigned_object_type}).")

    def get_kind_color(self):
        return JournalEntryKindChoices.colors.get(self.kind)


class ConfigRevision(models.Model):
    """
    An atomic revision of NetBox's configuration.
    """
    created = models.DateTimeField(
        auto_now_add=True
    )
    comment = models.CharField(
        max_length=200,
        blank=True
    )
    data = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Configuration data'
    )

    def __str__(self):
        return f'Config revision #{self.pk} ({self.created})'

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        return super().__getattribute__(item)

    def activate(self):
        """
        Cache the configuration data.
        """
        cache.set('config', self.data, None)
        cache.set('config_version', self.pk, None)

    @admin.display(boolean=True)
    def is_active(self):
        return cache.get('config_version') == self.pk

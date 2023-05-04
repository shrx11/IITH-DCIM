from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _

from utilities.forms import BootstrapMixin, DateTimePicker, SelectDurationWidget
from utilities.utils import local_now

__all__ = (
    'ReportForm',
)


class ReportForm(BootstrapMixin, forms.Form):
    schedule_at = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(),
        label=_("Schedule at"),
        help_text=_("Schedule execution of report to a set time"),
    )
    interval = forms.IntegerField(
        required=False,
        min_value=1,
        label=_("Recurs every"),
        widget=SelectDurationWidget(),
        help_text=_("Interval at which this report is re-run (in minutes)")
    )

    def clean(self):
        scheduled_time = self.cleaned_data['schedule_at']
        if scheduled_time and scheduled_time < local_now():
            raise forms.ValidationError(_('Scheduled time must be in the future.'))

        # When interval is used without schedule at, raise an exception
        if self.cleaned_data['interval'] and not scheduled_time:
            self.cleaned_data['schedule_at'] = local_now()

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Annotate the current system time for reference
        now = local_now().strftime('%Y-%m-%d %H:%M:%S')
        self.fields['schedule_at'].help_text += f' (current time: <strong>{now}</strong>)'

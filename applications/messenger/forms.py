from base64 import b64encode

from django import forms
from django.core.validators import FileExtensionValidator

from .choices import MODE
from .reporting import SUMMARY_GROUP_BY, task_reporting_missive


class MissiveReportingForm(forms.Form):
    since = forms.DateField(
        label='Since',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )
    until = forms.DateField(
        label='Until',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'type': 'email'}),
        required=True,
    )
    mode = forms.MultipleChoiceField(
        label='Mode',
        choices=MODE,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    summary = forms.BooleanField(
        label='Summary',
        help_text=(
            'Add the totals per company to the email body, and a second CSV.'
        ),
        required=False,
    )
    margin = forms.FloatField(
        label='Margin (%)',
        help_text=(
            'Percentage added to the printing costs in the summary; postage'
            ' is always passed on at cost.'
        ),
        required=False,
        min_value=0,
        initial=0,
    )
    template = forms.FileField(
        label='Excel template',
        help_text=(
            'Optional xlsx template holding {{ tag }} placeholders: one filled'
            ' workbook per company is attached as a zip archive.'
        ),
        required=False,
        validators=[FileExtensionValidator(['xlsx'])],
    )

    def clean(self):
        cleaned_data = super().clean()
        since = cleaned_data.get('since')
        until = cleaned_data.get('until')

        if since and until and since > until:
            raise forms.ValidationError('The "Since" date cannot be after the "Until" date.')

        return cleaned_data

    def generate_report(self):
        """
        Generate a report based on the form data.
        """
        email = self.cleaned_data.get('email')
        since = self.cleaned_data.get('since')
        until = self.cleaned_data.get('until')
        mode = self.cleaned_data.get('mode')
        summary = self.cleaned_data.get('summary')
        template = self.cleaned_data.get('template')

        # The worker runs in another container, so the template travels with
        # the task rather than through a temporary file.
        if template:
            template = b64encode(template.read()).decode()

        # Generate the report
        report_file = task_reporting_missive(
            email=email,
            since=since,
            until=until,
            mode=mode,
            summary=SUMMARY_GROUP_BY if summary else None,
            template=template or None,
            margin=self.cleaned_data.get('margin') or 0.0,
        )

        return report_file

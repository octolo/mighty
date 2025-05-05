from django import forms
from .choices import MODE
from .reporting import task_reporting_missive


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

        # Generate the report
        report_file = task_reporting_missive(
            email=email,
            since=since,
            until=until,
            mode=mode,
        )

        return report_file

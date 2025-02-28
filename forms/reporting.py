from django import forms

from mighty.apps import MightyConfig
from mighty.forms.descriptors import ModelFormDescriptable


class ReportingForm(ModelFormDescriptable):
    def prepare_descriptor(self):
        fake_model = self._meta.model()
        reporting_choices = fake_model.reporting_choices
        self.fields['reporting'] = forms.ChoiceField(choices=reporting_choices)
        self.fields['file_type'] = forms.ChoiceField(
            required=True, choices=MightyConfig.reporting_content_type
        )

    class Meta:
        fields = ()

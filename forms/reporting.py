from django import forms
from mighty.apps import MightyConfig
from mighty.forms.descriptors import ModelFormDescriptable

class ReportingForm(ModelFormDescriptable):
    file_type = forms.ChoiceField(required=True, choices=MightyConfig.reporting_content_type)

    class Meta:
        fields = ("reporting_list",)

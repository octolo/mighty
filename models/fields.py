from django.db import models
from mighty.forms import fields

class DateField(models.DateField):
    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": fields.DateField,
                **kwargs,
            }
        )

class DateTimeField(models.DateTimeField):
    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": fields.DateTimeField,
                **kwargs,
            }
        )

class ForeignKey(models.ForeignKey):
    create_if_not_exist = False

    def __init__(self, to, on_delete, **kwargs):
        self.create_if_not_exist = kwargs.pop("create_if_not_exist", False)
        super().__init__(to, on_delete, **kwargs)

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": fields.ModelChoiceField,
                **kwargs,
            }
        )
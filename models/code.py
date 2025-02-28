"""
Model class
Add [code] field at the model
generate a unique code from a list of fields

[code_fields] list of field used to generate code
(get_code) get the code generate
(set_code) set the code generate
"""
import re

from django.db import models

from mighty.functions import generate_code, make_searchable


class Code(models.Model):
    code = models.CharField(max_length=50, blank=True, null=True, editable=False)
    model_activate_code = True

    class Meta:
        abstract = True

    @property
    def unique_rule(self):
        for rule in self._meta.unique_together:
            if 'code' in rule:
                return {field: getattr(self, field) for field in rule}
        return None

    def get_code(self):
        return generate_code(self, rule=self.unique_rule)

    def set_code(self):
        if self.id and not self.code:
            self.code = self.get_code()

    def save(self, *args, **kwargs):
        self.set_code()
        super().save(*args, **kwargs)


class BasedFields(Code):
    code_fields = []

    class Meta:
        abstract = True

    def get_code(self):
        fields = [getattr(self, field) for field in self.code_fields if hasattr(self, field)]
        code = ''.join([field[0] for field in fields if re.match(re.compile(r'[a-zA-Z0-9]+'), field)])
        code = make_searchable(code).upper()
        return generate_code(self, code=code, rule=self.unique_rule)

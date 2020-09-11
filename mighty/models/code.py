"""
Model class
Add [code] field at the model
generate a unique code from a list of fields

[code_fields] list of field used to generate code
(get_code) get the code generate
(set_code) set the code generate
"""
from django.db import models
from mighty.functions import make_searchable, split_comment
import re

class Code(models.Model):
    code_fields = []
    code = models.CharField(max_length=50, blank=True, null=True, editable=False)

    class Meta:
        abstract = True

    def get_code(self):
        code = " ".join([getattr(self, field) for field in self.code_fields if hasattr(self, field)])
        if code:
            code = "".join([word[0] for word in code.strip().split() if re.match(re.compile('[a-zA-Z0-9]+'), word)])
            return make_searchable("%s%s" % (code, int(len(code))+int(self.id))).upper()
        return None
    
    def set_code(self):
        if self.id is not None:
            self.code = self.get_code()

    def save(self, *args, **kwargs):
        self.set_code()
        super().save(*args, **kwargs)
from django.db import models
from django.template.defaultfilters import slugify

from mighty.functions import getattr_recursive


def NamedIdModel(**kwargs):
    def decorator(obj):
        class NewClass(obj):
            Qnamed_id = kwargs.get('Qfields', ())
            named_id_fields = kwargs.get('fields', ())
            named_id = models.CharField(max_length=255, blank=kwargs.get('blank', True), null=kwargs.get('null', True))

            @property
            def model_fields(self):
                return {field.name: field.__class__.__name__ for field in self._meta.get_fields()}

            @property
            def Qnamedfields(self):
                return self.Qnamed_id or self.named_id_fields

            @property
            def Qasfield(self):
                return {field: getattr(self, field) for field in self.Qnamedfields if field in self.model_fields}

            @property
            def qs_named_id(self):
                return self.qs_not_self.filter(**self.Qasfield)

            @property
            def count_named_id(self):
                return 0 if kwargs.get('start0') else self.qs_named_id.count()

            @property
            def named_id_exist(self):
                return self.qs_named_id.filter(named_id=self.named_id).count()

            def set_named_id(self, offset=0):
                base_name = '-'.join([str(getattr_recursive(self, field)) for field in self.named_id_fields if getattr_recursive(self, field)])
                named_id = slugify(base_name)
                count = self.count_named_id + offset
                self.named_id = f'{named_id}-{count + 1}' if count > 0 else named_id
                if self.named_id_exist: self.set_named_id(offset + 1)

            class Meta(obj.Meta):
                abstract = obj._meta.abstract

        NewClass.__name__ = obj.__name__
        return NewClass
    return decorator

from django.db import models
from django.template.defaultfilters import slugify

def NamedIdModel(**kwargs):
    def decorator(obj):
        class NamedIdModel(obj):
            Qnamed_id = kwargs.get("Qfields", ())
            named_id_fields = kwargs.get("fields", ())
            named_id = models.CharField(max_length=255, blank=kwargs.get("blank", True), null=kwargs.get("null", True))

            class Meta(obj.Meta):
                abstract = True

            @property
            def Qnamedfields(self):
                return self.Qnamed_id or self.named_id_fields

            @property
            def Qasfield(self):
                return {field: getattr(self, field) for field in self.Qnamedfields}

            @property
            def count_named_id(self):
                return self.qs_not_self.filter(**self.Qasfield).count()

            @property
            def named_id_exist(self):
                return type(self).objects.filter(**self.Qasfield, named_id=self.named_id).count()

            def set_named_id(self, offset=0):
                base_name = "-".join([str(getattr(self, field)) for field in self.named_id_fields])
                named_id = slugify(base_name)
                count = self.count_named_id+offset
                self.named_id = "%s-%s" % (named_id, count+1) if count > 0 else named_id
                print(self.named_id_exist)
                if self.named_id_exist: self.set_named_id(offset+1)

        return NamedIdModel
    return decorator

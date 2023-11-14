from django.db import models
from django.template.defaultfilters import slugify

def NamedIdModel(**kwargs):
    def decorator(obj):
        obj.Qnamed_id = kwargs.get("Qfields", ())
        obj.named_id_fields = kwargs.get("fields", ())
        obj.add_to_class("named_id", models.CharField(max_length=255, blank=kwargs.get("blank", True), null=kwargs.get("null", True)))

        @property
        def Qnamedfields(self):
            return self.Qnamed_id or self.named_id_fields
        obj.Qnamedfields = Qnamedfields

        @property
        def Qasfield(self):
            return {field: getattr(self, field) for field in self.Qnamedfields}
        obj.Qasfield = Qasfield

        @property
        def qs_named_id(self):
            return self.qs_not_self.filter(**self.Qasfield)
        obj.qs_named_id = qs_named_id

        @property
        def count_named_id(self):
            return 0 if kwargs.get("start0") else self.qs_named_id.count()
        obj.count_named_id = count_named_id

        @property
        def named_id_exist(self):
            return self.qs_named_id.filter(named_id=self.named_id).count()
        obj.named_id_exist = named_id_exist

        def set_named_id(self, offset=0):
            base_name = "-".join([str(getattr(self, field)) for field in self.named_id_fields])
            named_id = slugify(base_name)
            count = self.count_named_id+offset
            self.named_id = "%s-%s" % (named_id, count+1) if count > 0 else named_id
            if self.named_id_exist: self.set_named_id(offset+1)
        obj.set_named_id = set_named_id

        return obj
    return decorator

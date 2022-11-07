from django.db import models
from django.template.defaultfilters import slugify

def NamedIdModel(**kwargs):
    def decorator(obj):
        class NamedIdModel(obj):
            named_id_fields = kwargs.get("fields", ())
            named_id = models.CharField(max_length=255, blank=kwargs.get("blank", True), null=kwargs.get("null", True))

            class Meta(obj.Meta):
                abstract = True

            def set_named_id(self):
                base_name = "-".join([getattr(self, field) for field in self.named_id_fields])
                named_id = slugify(base_name)
                count = self.qs_not_self.count()
                self.named_id = "%s-%s" % (named_id, count+1) if count > 0 else named_id

        return NamedIdModel
    return decorator

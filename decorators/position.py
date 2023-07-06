from django.db import models
from django.template.defaultfilters import slugify

def PositionModel(**kwargs):
    def decorator(obj):
        class PositionModel(obj):
            Qposition = kwargs.get("Qfields", ())
            position_fields = kwargs.get("fields", ())
            position = models.PositiveIntegerField(blank=kwargs.get("blank", True), null=kwargs.get("null", True))

            class Meta(obj.Meta):
                abstract = True

            @property
            def position_qs(self):
                return self.qs_not_self.filter(**self.Qasfield)

            @property
            def Qpositionfields(self):
                return self.Qposition or self.position_fields

            @property
            def Qasfield(self):
                return {field: getattr(self, field) for field in self.Qpositionfields}

            @property
            def count_position(self):
                return self.position_qs.filter(**self.Qasfield).count()

            @property
            def position_exist(self):
                return self.position_qs.filter(position=self.position).count()

            def set_position(self, offset=1):
                if not self.position:
                    count = self.count_position
                    self.position = count+offset

            def on_delete_position(self):
                qs = self.position_qs.filter(position__gt=self._unmodified.position)
                for i,p in enumerate(qs): qs[i].position-=1
                type(self).objects.bulk_update(qs, ["position"])

        return PositionModel
    return decorator

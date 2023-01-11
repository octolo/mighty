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
            def Qpositionfields(self):
                return self.Qposition or self.position_fields

            @property
            def Qasfield(self):
                return {field: getattr(self, field) for field in self.Qpositionfields}

            @property
            def count_position(self):
                print(self.Qasfield)
                for s in self.qs_not_self:
                    print(s.id)
                return self.qs_not_self.filter(**self.Qasfield).count()

            @property
            def position_exist(self):
                return type(self).objects.filter(**self.Qasfield, position=self.position).count()

            def set_position(self, offset=1):
                if not self.position:
                    count = self.count_position
                    print(count)
                    self.position = count+offset

        return PositionModel
    return decorator

from django.db import models
from mighty.models.base import Base
from mighty import translates as _

class AnticipateModel(Base):
    object_id = models.ForeignKey('', on_delete=models.CASCADE)
    field = models.CharField(_.field, max_length=255, db_index=True)
    value = models.BinaryField(_.value)
    fmodel = models.CharField(_.fmodel, max_length=255)
    date_begin = models.DateField(_.date_begin)
    date_end = models.DateField(_.date_end, null=True, blank=True)
    user = models.CharField(max_length=255)

    class Meta:
        abstract = True
        verbose_name = _.v_anticipate
        verbose_name_plural = _.vp_anticipate
        ordering = ['-date_begin']

    @property
    def get_value(self):
        return self.value.decode('utf-8')
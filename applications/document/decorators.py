from django.db import models

def ModelTemplate(**kwargs):
    def decorator(obj):

        class DTModel(obj):
            sync_fields = kwargs.get('sync_fields', [])
            based_on = models.ForeignKey(kwargs.get('based_fk', 'self'),
                on_delete=kwargs.get('on_delete', models.SET_NULL),
                related_name=kwargs.get('based_related_name', 'based_on_set'),
                blank=kwargs.get('based_blank', True),
                null=kwargs.get('based_null', True),
            )
            config = models.JSONField(null=True, blank=True) 
            context = models.JSONField(null=True, blank=True)
            
            if kwargs.get('can_sign', False):
                signatory = models.ManyToManyField(kwargs.get('signatory_m2m'),
                    related_name=kwargs.get('signatory_related_name', 'signatory_set'),
                    blank=kwargs.get('signatory_blank', True),
                    null=kwargs.get('signatory_null', True),
                )
                is_signed = models.BooleanField(default=False)
            
            class Meta(obj.Meta):
                abstract = True

            def fields_synchronization(self):
                if self.based_on and self.pk is None:
                    for field in self.sync_fields:
                        based_field = getattr(self.based_on, field)
                        if based_field and not getattr(self, field):
                            setattr(self, field, based_field)

            def check_signatory(self):
                pass

            def save(self, *args, **kwargs):
                self.fields_synchronization()
                self.check_signatory()
                super().save(*args, **kwargs)

        return DTModel
    return decorator
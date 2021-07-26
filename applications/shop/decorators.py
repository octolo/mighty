from django.db import models
from django.utils import timezone

def EnableSubscription(**kwargs):
    def decorator(obj):

        class SUBModel(obj):
            subscription = models.ForeignKey('mighty.Subscription',
                on_delete=kwargs.get('on_delete', models.SET_NULL), 
                related_name=kwargs.get('related_name', 'subscription_set'),
                blank=kwargs.get('blank', True),
                null=kwargs.get('null', True),
            )
            valid_payment_methods = models.DateField(blank=True, null=True, editable=False)
            valid_subscription = models.DateField(blank=True, null=True, editable=False)
            

            class Meta(obj.Meta):
                abstract = True

            def set_valid_date_pm(self, pm):
                if pm.is_valid:
                    if self.valid_payment_methods is None or pm.date_valid > self.valid_payment_methods:
                        self.valid_payment_methods = pm.date_valid

            def set_valid_valid_payment_methods(self):
                pms = list(filter(True, [pm.is_valid() for pm in self.payment_method.all()]))
                for pm in pms:
                    self.set_valid_date_pm(pm)

            @property
            def subscription_active(self):
                if self.subscription:
                    return True if self.valid_subscription < timezone.now else False
                return False

            def save(self, *args, **kwargs):
                self.set_valid_valid_payment_methods()
                super().save(*args, **kwargs)

        return SUBModel
    return decorator
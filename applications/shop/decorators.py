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
            valid_payment_methods = models.PositiveIntegerField(default=0, editable=False)

            class Meta(obj.Meta):
                abstract = True

            #def set_last_subscription(self):
            #    self.last_subscription = getattr(self,kwargs.get('related_name', 'subscription_set')).order_by('-date_start').last()

            def set_valid_valid_payment_methods(self):
                self.valid_payment_methods = len(list(filter(True, [pm.is_valid() for pm in self.payment_method.all()])))

            @property
            def subscription_active(self):
                if self.subscription:
                    now = timezone.now
                    return True if now >= self.subscription.date_start and now <= self.subscription.date_end else False
                return False

            def save(self, *args, **kwargs):
                self.set_valid_valid_payment_methods()
                super().save(*args, **kwargs)

        return SUBModel
    return decorator
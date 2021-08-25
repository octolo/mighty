from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from mighty.models.base import Base
from mighty.applications.shop.apps import ShopConfig

def GroupOrUser(**kwargs):
    def decorator(obj):
        class GOUModel(obj):
            if ShopConfig.subscription_for == 'group':
                group = models.ForeignKey(ShopConfig.group, 
                    on_delete=kwargs.get('on_delete', models.SET_NULL), 
                    related_name=kwargs.get('related_name', 'group_set'),
                    blank=kwargs.get('blank', False),
                    null=kwargs.get('null', False))
            else:
                user = models.ForeignKey(get_user_model(), 
                    on_delete=kwargs.get('on_delete', models.SET_NULL), 
                    related_name=kwargs.get('related_name', 'user_set'),
                    blank=kwargs.get('blank', False),
                    null=kwargs.get('null', False))

            class Meta(obj.Meta):
                abstract = True

            @property
            def group_or_user(self):
                return self.group if hasattr(self, 'group') else self.user

            def set_group_or_user(self, obj):
                if ShopConfig.subscription_for == 'group':
                    self.group = obj
                else:
                    self.user = obj

        return GOUModel
    return decorator

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

            #def set_valid_date_pm(self, pm):
            #    if pm.is_valid:
            #        if self.valid_payment_methods is None or pm.date_valid > self.valid_payment_methods:
            #            self.valid_payment_methods = pm.date_valid

            #def set_valid_valid_payment_methods(self):
            #    for pm in self.payment_method.all():
            #        self.set_valid_date_pm(pm)

            @property
            def subscription_active(self):
                return True if self.subscription and self.subscription.is_active else False

            def save(self, *args, **kwargs):
                #self.set_valid_valid_payment_methods()
                super().save(*args, **kwargs)

        return SUBModel
    return decorator
from django.conf import settings
from rest_framework.serializers import ModelSerializer
from mighty.models import Subscription
from mighty.applications.shop import fields

class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('uid',) + fields.subscription

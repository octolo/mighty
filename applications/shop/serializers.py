from django.conf import settings
from rest_framework.serializers import ModelSerializer, SerializerMethodField, DateField
from mighty.models import Subscription, PaymentMethod, Offer
from mighty.applications.shop import fields

class PaymentMethodSerializer(ModelSerializer):
    date_valid = DateField(format="%m/%Y", required=False)
    month = DateField(format="%m", required=False)
    year = DateField(format="%Y", required=False)

    class Meta:
        model = PaymentMethod
        fields = ('uid',) + fields.payment_method

class OfferSerializer(ModelSerializer):
    class Meta:
        model = Offer
        fields = ('uid', 'name', 'frequency', 'duration', 'price', 'named_id')

class SubscriptionSerializer(ModelSerializer):
    offer = OfferSerializer()
    service = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('uid', 'next_paid', 'date_end', 'date_start', 'offer', 'service', 'is_active')

    def get_service(self, obj):
        return obj.cache

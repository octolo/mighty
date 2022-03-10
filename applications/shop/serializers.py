from django.conf import settings
from rest_framework.serializers import ModelSerializer, SerializerMethodField, DateField
from mighty.models import Subscription, PaymentMethod, Offer, ShopService, ShopItem
from mighty.applications.shop import fields

class ShopServiceSerializer(ModelSerializer):
    class Meta:
        model = ShopService
        fields = fields.service + ("real_tax", "calc_tax", "price_ht", "price_ttc")

class ShopItemSerializer(ModelSerializer):
    class Meta:
        model = ShopItem
        fields = fields.item + ("real_tax", "calc_tax", "price_ht", "price_ttc")

class PaymentMethodSerializer(ModelSerializer):
    date_valid = DateField(format="%m/%Y", required=False)
    month = DateField(format="%m", required=False)
    year = DateField(format="%Y", required=False)

    class Meta:
        model = PaymentMethod
        fields = ('uid',) + fields.payment_method

class OfferSerializer(ModelSerializer):
    service = ShopServiceSerializer(many=True)
    service_tenant = ShopServiceSerializer()

    class Meta:
        model = Offer
        fields = fields.offer + ("image_url", "real_tax", "calc_tax", "price_ht", "price_ttc", "service_tenant")

class SubscriptionSerializer(ModelSerializer):
    offer = OfferSerializer()
    service = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('uid', 'next_paid', 'date_end', 'date_start', 'offer', 'service', 'is_active')

    def get_service(self, obj):
        return obj.cache

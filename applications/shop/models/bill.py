from django.db import models
from django.utils.module_loading import import_string
from django.utils.text import get_valid_filename

from mighty.models.base import Base
from mighty.applications.shop.apps import ShopConfig
from mighty.applications.shop.decorators import GroupOrUser
from mighty.applications.document import generate_pdf

@GroupOrUser(related_name="group_bill", blank=True, null=True)
class Bill(Base):
    amount = models.FloatField(blank=True, null=True)
    end_amount = models.FloatField(blank=True, null=True)
    date_payment = models.DateTimeField(blank=True, null=True, editable=False)
    paid = models.BooleanField(default=False, editable=False)
    payment_id = models.CharField(max_length=255, blank=True, null=True, editable=False)
    subscription = models.ForeignKey('mighty.Subscription', on_delete=models.SET_NULL, blank=True, null=True, related_name='subscription_bill', editable=False)
    method = models.ForeignKey('mighty.PaymentMethod', on_delete=models.SET_NULL, blank=True, null=True, related_name='method_bill', editable=False)
    discount = models.ManyToManyField('mighty.Discount', blank=True, related_name='discount_bill')
    end_discount = models.FloatField(blank=True, null=True)
    backend = models.CharField(max_length=255, blank=True, null=True, editable=False)
    need_action = models.CharField(max_length=25, blank=True, null=True, editable=False)
    
    class Meta(Base.Meta):
        abstract = True

    def __str__(self):
        return "%s - %s" % (self.group, self.subscription)

    @property
    def offer(self):
        return self.subscription.offer

    @property
    def follow_id(self):
        return "msbID_%s.%s" % (self.uid, self.pk)

    def calcul_discount(self):
        amount = self.amount
        amount -= sum([discount.amount for discount in self.discount.filter(is_percent=False)])
        for discount in self.discount.filter(is_percent=True).order_by('-amount'):
            amount -= (amount/100*discount.amount)
        self.end_amount = round(amount, 2)
        self.end_discount = round(self.amount-self.end_amount, 2)

    def try_to_charge(self):
        if not self.paid and self.method is not None and self.method.is_valid:
            self.to_charge()

    def to_charge(self):
        backend = import_string(ShopConfig.invoice_backend)(self, ShopConfig.invoice_backend)
        backend.add_pm()
        backend.try_to_charge()

    def pre_update(self):
        self.calcul_discount()

    # PDF
    @property
    def bill_pdf_url(self):
        return self.get_url('pdf', arguments=self.url_args)

    @property
    def bill_pdf_context(self):
        return {"group_or_user": self.group_or_user, "offer": self.offer, "subscription": self.subscription, "bill": self.bill}

    @property
    def bill_pdf_name(self):
        return get_valid_filename("%s_%s.pdf" % (self.group_or_user, self.offer))

    @property
    def bill_pdf_content(self):
        return ShopConfig.invoice_template

    @property
    def bill_pdf_data(self):
        return {
            "file_name": self.bill_pdf_name,
            "context": self.bill_pdf_context,
            "content": self.bill_pdf_content,
        }

    @property
    def bill_to_pdf(self):
        pdf_data = self.bill_pdf_data
        final_pdf, tmp_pdf = generate_pdf(**pdf_data)
        tmp_pdf.close()
        return final_pdf


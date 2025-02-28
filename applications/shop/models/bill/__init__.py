from django.db import models

from mighty.applications.shop import choices as _c
from mighty.applications.shop import translates as _
from mighty.applications.shop.apps import ShopConfig
from mighty.applications.shop.decorators import GroupOrUser
from mighty.applications.shop.models.bill.charge import ChargeModel
from mighty.applications.shop.models.bill.pdf import PDFModel
from mighty.fields import JSONField
from mighty.models.base import Base


@GroupOrUser(
    related_name='group_bill', on_delete=models.SET_NULL, null=True, blank=True
)
class Bill(Base, PDFModel, ChargeModel):
    # Related
    subscription = models.ForeignKey(
        'mighty.Subscription',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subscription_bill',
        editable=False,
    )
    service = models.ManyToManyField(
        'mighty.ShopService', blank=True, related_name='service_bill'
    )
    discount = models.ManyToManyField(
        'mighty.Discount', blank=True, related_name='discount_bill'
    )
    method = models.ForeignKey(
        'mighty.PaymentMethod',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='method_bill',
        editable=False,
    )

    # Date
    date_paid = models.DateField(blank=True, null=True)
    date_payment = models.DateTimeField(blank=True, null=True, editable=False)

    # Status
    paid = models.BooleanField(default=False, editable=False)
    numero = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(
        max_length=25, choices=_c.BILL_STATUS, default=_c.NOTHING
    )

    items = JSONField(default=list)

    # Backend
    backend = models.CharField(
        max_length=255, blank=True, null=True, editable=False
    )
    payment_id = models.CharField(
        max_length=255, blank=True, null=True, editable=False, unique=True
    )
    action = models.TextField(blank=True, null=True, editable=False)

    # Price
    override_price = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=2
    )
    amount = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=2
    )
    end_discount = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=2
    )
    end_amount = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=2
    )
    tva_calc_month = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=2
    )
    total_calc_month = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=2
    )

    class Meta(Base.Meta):
        abstract = True
        unique_together = ShopConfig.bill_unique_together

    def __str__(self):
        return f'{self.group} - {self.subscription}'

    @property
    def offer(self):
        return self.subscription.offer

    @property
    def add_item(self, *args, **kwargs):
        self.items.append({
            'description': kwargs.get('description'),
            'reference': kwargs.get('reference'),
            'quantity': kwargs.get('quantity'),
            'unique_price_ht_month': kwargs.get('unique_price_ht_month'),
            'amount_ht_month': kwargs.get('amount_ht_month'),
            'tva': kwargs.get('tva'),
            'amount_ttc_month': kwargs.get('amount_ttc_month'),
        })

    @property
    def tva_month_items(self):
        return sum(amount_ht_month for item in self.items)

    @property
    def tva_calc_year(self):
        return self.tva_month_items * 12

    @property
    def total_month_items(self):
        return sum(amount_ttc_month for item in self.items)

    @property
    def total_calc_year(self):
        return self.total_month_items * 12

    def calcul_from_items(self):
        self.tva_calc_month = self.tva_month_items
        self.total_calc_month = self.total_month_items

    def set_numero(self):
        if not self.numero:
            nbr = type(self).objects.filter(group=self.group).count() + 1
            if nbr > 100:
                self.numero = '0' + str(nbr)
            elif nbr > 10:
                self.numero = '00' + str(nbr)
            else:
                self.numero = '000' + str(nbr)

    @property
    def follow_id(self):
        return f'msbID_{self.uid}.{self.pk}'

    @property
    def bill_numero(self):
        return (
            f'{self.date_payment.year}-{self.date_payment.month}{self.numero}'
        )

    def calcul_discount(self):
        if self.override_price:
            self.end_amount = self.override_price
        else:
            amount = self.amount
            amount -= sum(
                discount.amount
                for discount in self.discount.filter(is_percent=False)
            )
            for discount in self.discount.filter(is_percent=True).order_by(
                '-amount'
            ):
                amount -= amount / 100 * discount.amount
            self.end_amount = round(amount, 2)
            self.end_discount = round(self.amount - self.end_amount, 2)

    def pre_save(self):
        self.set_numero()
        if self.status == _c.CHECK:
            self.check_bill_status()

    def pre_update(self):
        self.calcul_discount()
        if self.status == _c.CHARGE:
            self.to_charge()

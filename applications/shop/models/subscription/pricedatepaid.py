from datetime import datetime

from dateutil.relativedelta import relativedelta


class PriceDatePaid:
    @property
    def price_tenant(self):
        if self.group_or_user:
            return self.offer.real_price_tenant * self.group_or_user.nbr_tenant
        return 0

    @property
    def discount_amount(self):
        return self.bill.end_discount

    @property
    def price_full(self):
        return self.offer.real_price + self.offer.real_price_tenant

    # Date
    def get_date_month(self):
        return self.next_paid + relativedelta(months=1)

    def get_date_year(self):
        return self.next_paid + relativedelta(months=12)

    def get_date_oneshot(self):
        return date.today()

    def set_date_by_frequency(self):
        self.next_paid = getattr(self, f'get_date_{self.offer.frequency.lower()}')() if self.next_paid else datetime.now

    def set_date_on_paid(self):
        self.set_date_by_duration() if self.offer.duration else self.set_date_by_frequency()

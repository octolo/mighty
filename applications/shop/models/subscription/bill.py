from datetime import date, datetime

from mighty.applications.shop import choices as _c


class Bill:
    def create_bill(self):
        self.logger.info('generate a new bill for subscription: %s' % self.pk)
        bill = self.subscription_bill.create(
            amount=self.price_full,
            group=self.group_or_user,
            subscription=self,
            method=self.method,
            date_payment=self.next_paid,
        )
        bill.discount.add(*self.discount.filter(date_end__gt=datetime.now()).order_by('-amount'))
        bill.status = _c.CHARGE if bill.date_payment <= date.today() else _c.NOTHING
        bill.save()
        self.bill = bill
        self.save()
        return True if bill.date_payment <= date.today() else False

    def prepare_bill(self):
        if not self.bill or self.bill.date_paid != self.next_paid:
            return self.create_bill()
        return False

    def should_bill(self):
        if not self.bill:
            self.next_paid = date.today()
        return self.prepare_bill()

    def do_bill(self):
        if self.should_bill():
            self.set_date_by_frequency()
            self.prepare_bill()
        return self.bill

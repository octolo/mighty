from datetime import datetime, date

class Bill:
    @property
    def bill_is_paid(self):
        return self.bill.paid if self.bill else False

    @property
    def should_bill(self):
        if self.method:
            if not self.bill:
                self.next_paid = date.today()
            if self.offer.frequency != 'ONUSE':
                return True if not self.next_paid or self.next_paid <= date.today() else False
        return False

    def do_bill(self):
        if self.should_bill:
            self.logger.info('generate a new bill for subscription: %s' % self.pk)
            bill = self.subscription_bill.create(amount=self.price_full, group=self.group_or_user, subscription=self, method=self.method)
            bill.discount.add(*self.discount.filter(date_end__gt=datetime.now()).order_by('-amount'))
            self.bill = bill
            self.save()
        return self.bill


    def update_bill(self):
        if not self.bill.paid:
            self.bill.method = self.method
            self.bill.discount.add(*self.discount.filter(date_end__gt=datetime.now()).order_by('-amount'))
            self.bill.del_cache('payment_method')
            self.bill.save()


    def on_bill_paid(self):
        if self.offer.frequency != 'ONUSE':
            pass
        else:
            self.coin+=1
            self.save()
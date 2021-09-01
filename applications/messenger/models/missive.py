from django.db import models
from django.utils.module_loading import import_string

from mighty.applications.messenger import choices, translates as _, send_missive
from mighty.functions import masking_email, masking_phone
from mighty.applications.messenger.models.abstracts import MessengerModel
from mighty.applications.address.models import AddressNoBase

class Missive(MessengerModel, AddressNoBase):
    backend = models.CharField(max_length=255, editable=False)
    subject = models.CharField(max_length=255)
    msg_id = models.CharField(max_length=255, blank=True, null=True)

    response = models.TextField(blank=True, null=True, editable=False)
    partner_id = models.CharField(max_length=255, blank=True, null=True, editable=False)
    code_error = models.CharField(max_length=255, blank=True, null=True, editable=False)
    trace = models.TextField(blank=True, null=True, editable=False)
    
    class Meta(MessengerModel.Meta):
        abstract = True
        verbose_name = "missive"
        verbose_name_plural = "missives"
        permissions = [('can_check', _.permission_check),]
        ordering = ['-date_create',]

    def __str__(self):
        return '%s (%s)' % (self.masking, self.subject)

    def need_to_send(self):
        if self.status == choices.STATUS_PREPARE and self.mode != choices.MODE_WEB:
            send_missive(self)

    def clear_errors(self):
        self.trace = None
        self.code_error = None

    def to_sent(self):
        self.clear_errors()
        self.status = choices.STATUS_SENT

    def get_backend(self):
        backend = import_string(self.backend)()
        return backend

    def check_status(self):
        backend = self.get_backend()
        return getattr(backend, 'check_%s' % self.mode.lower())(self)
#
#    def email(self):
#        return self.user.email
#    email.short_description = _.email
#    email.admin_order_field = 'user__email'
#
#    def phone(self):
#        return self.user.phone
#    phone.short_description = _.phone
#    phone.admin_order_field = 'user__phone'
#
#    def postal(self):
#        return self.user.address
#    postal.short_description = _.postal
#    postal.admin_order_field = 'user__address'
#

from django.db import models
from django.utils.module_loading import import_string

from mighty.applications.messenger import choices, translates as _, send_missive
from mighty.functions import masking_email, masking_phone
from mighty.applications.messenger.models.abstracts import MessengerModel
from mighty.applications.address.models import AddressNoBase

class Missive(MessengerModel, AddressNoBase):
    backend = models.CharField(max_length=255, editable=False)
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
        if self.status in (choices.STATUS_PREPARE, choices.STATUS_FILETEST):
            send_missive(self)

    def clear_errors(self):
        self.trace = None
        self.code_error = None

    def to_sent(self):
        self.clear_errors()
        self.status = choices.STATUS_SENT

    def get_backend(self):
        backend = import_string("%s.MissiveBackend" % self.backend)(missive=self)
        return backend

    def check_status(self):
        backend = self.get_backend()
        return getattr(backend, 'check_%s' % self.mode.lower())()

    @property
    def js_admin(self):
        backend = self.get_backend()
        return backend.js_admin

    @property
    def url_viewer(self):
        from django.urls import reverse
        return reverse('messenger-email-viewer', args=[self.uid])

    def on_raw_ready(self):
        if not self.target:
            if self.raw_address:
                self.target = self.raw_address

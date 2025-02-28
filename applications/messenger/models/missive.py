from django.db import models
from django.utils.module_loading import import_string

from mighty.applications.address.models import AddressNoBase
from mighty.applications.messenger import choices, send_missive
from mighty.applications.messenger import translates as _
from mighty.applications.messenger.decorators import HeritToMessenger


@HeritToMessenger(related_name='missive_to_content_type', backend_blank=False, backend_null=False)
class Missive(AddressNoBase):
    msg_id = models.CharField(max_length=255, blank=True, null=True)
    response = models.TextField(blank=True, null=True, editable=False)
    partner_id = models.CharField(max_length=255, blank=True, null=True, editable=False)
    code_error = models.CharField(max_length=255, blank=True, null=True, editable=False)
    trace = models.TextField(blank=True, null=True, editable=False)
    price_config = models.JSONField(default=dict)
    price_info = models.JSONField(default=dict)

    class Meta:
        abstract = True
        verbose_name = 'missive'
        verbose_name_plural = 'missives'
        permissions = [('can_check', _.permission_check)]
        ordering = ['-date_create']

    def __str__(self):
        return f'{self.masking} ({self.mode})'

    def need_to_send(self):
        if self.status in {choices.STATUS_PREPARE, choices.STATUS_FILETEST}:
            send_missive(self)

    def clear_errors(self):
        self.trace = None
        self.code_error = None

    def to_sent(self):
        self.clear_errors()
        self.status = choices.STATUS_SENT

    def get_backend(self):
        return import_string(f'{self.backend}.MissiveBackend')(missive=self)

    def check_documents(self):
        return self.get_backend().check_documents()

    def check_status(self):
        backend = self.get_backend()
        return getattr(backend, f'check_{self.mode.lower()}')()

    def cancel_missive(self):
        return self.get_backend().cancel()

    @property
    def js_admin(self):
        backend = self.get_backend()
        return backend.js_admin

    @property
    def is_read(self):
        return self.status == choices.STATUS_OPEN

    @property
    def url_viewer(self):
        from django.urls import reverse
        return reverse('messenger-email-viewer', args=[self.uid])

    def on_raw_ready(self):
        if not self.target and self.raw_address:
            self.target = self.raw_address

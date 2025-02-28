import sib_api_v3_sdk
from django.conf import settings

from mighty.applications.messenger.backends import MissiveBackend
from mighty.apps import MightyConfig


class MissiveBackend(MissiveBackend):
    CONFSIB = False
    APISIB = False
    APISMS = False

    @property
    def conf_sib(self):
        if not self.CONFSIB:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = settings.SENDINBLUE_APIKEY
            self.CONFSIB = configuration
        return self.CONFSIB

    @property
    def api_sib(self):
        if not self.APISIB:
            self.APISIB = sib_api_v3_sdk.ApiClient(self.conf_sib)
        return self.APISIB

    @property
    def api_sms(self):
        if not self.APISMS:
            self.APISMS = sib_api_v3_sdk.TransactionalSMSApi(self.api_sib)
        return self.APISMS

    def use_api_sms(self, missive):
        api_instance = self.api_sms
        send_transac_sms = sib_api_v3_sdk.SendTransacSms(
            sender=MightyConfig.domain.lower(),
            recipient=self.missive.target,
            content=self.missive.txt,
            type='transactionnal',
        )
        try:
            api_response = api_instance.send_transac_sms(send_transac_sms)
            self.missive.trace = str(api_response)
            return True
        except Exception as e:
            self.missive.trace(str(e))
            return False

    def send_sms(self):
        over_target = setting('MISSIVE_PHONE', False)
        self.missive.target = over_target or self.missive.target
        self.missive.status = choices.STATUS_SENT
        if setting('MISSIVE_SERVICE', False):
            if not self.use_api_sms(self.missive):
                self.missive.status = choices.STATUS_ERROR
        self.missive.save()
        return self.missive.status

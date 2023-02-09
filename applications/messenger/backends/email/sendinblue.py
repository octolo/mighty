from mighty.applications.messenger.backends import MissiveBackend
from mighty.functions import setting
from mighty.apps import MightyConfig
from mighty.applications.messenger import choices
from django.core.mail.message import make_msgid
import requests, json, base64, sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

class MissiveBackend(MissiveBackend):
    APIKEY = setting('SENDINBLUE_KEY', False)
    APIURL = "https://api.sendinblue.com/v3/smtp/email"
    in_error = False
    api_instance_cache = None

    @property
    def api_instance(self):
        if not self.api_instance_cache:
            configuration = sib_api_v3_sdk.Configuration()
            print(self.APIKEY)
            configuration.api_key['api-key'] = self.APIKEY
            self.api_instance_cache = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        return self.api_instance_cache

    def email_attachments(self):
        attachments = []
        if self.missive.attachments:
            logs = []
            for document in self.missive.attachments:
                if setting('MISSIVE_SERVICE', False):
                    attachements.append({
                        "content": base64.b64encode(document.read()),
                        "name": os.path.basename(document.name),
                    })
                logs.append(os.path.basename(document.name))
            self.missive.logs['attachments'] = logs
        return attachments

    def send_email(self):
        over_target = setting('MISSIVE_EMAIL', False)
        self.missive.target = over_target if over_target else self.missive.target
        self.logger.info("Email - from : %s, to : %s, reply : %s" %
            (self.sender_email, self.missive.target, self.reply_email))
        if True:
            self.missive.msg_id = make_msgid()
            data = {
                "to": [{"email": self.missive.target}],
                "reply_to": {"email": self.reply_email, "name": self.reply_name},
                "headers": { "charset":"iso-8859-1"},
                "sender": {"email": self.missive.sender, "name": self.missive.name},
                "subject": self.missive.subject,
            }
            if self.missive.html_format: data["html_content"] = self.missive.html_format
            else: data["text_content"] = str(self.missive.txt)
            attachs = self.email_attachments()
            if len(attachs): data["attachment"] = attachs
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**data)
            try:
                api_response = self.api_instance.send_transac_email(send_smtp_email)
                print(api_response)
            except ApiException as e:
                print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        self.missive.to_sent()
        self.missive.save()
        return self.missive.status

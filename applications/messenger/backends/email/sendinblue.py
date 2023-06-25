from django.core.mail.message import make_msgid
from mighty.applications.messenger.backends import MissiveBackend
from mighty.applications.messenger import choices as _c
from mighty.functions import setting
from mighty.apps import MightyConfig
import os, base64, sib_api_v3_sdk, json

class MissiveBackend(MissiveBackend):
    APIKEY = setting('SENDINBLUE_KEY', False)
    APIURL = "https://api.sendinblue.com/v3/smtp/email"
    in_error = False
    api_instance_cache = None

    STATUS = {
        "bounces": _c.STATUS_ERROR,
        "hardBounces": _c.STATUS_ERROR,
        "softBounces": _c.STATUS_ERROR,
        "delivered": _c.STATUS_SENT,
        "spam": _c.STATUS_ERROR,
        "requests": _c.STATUS_PROCESSED,
        "opened": _c.STATUS_OPEN,
        "clicks": _c.STATUS_OPEN,
        "invalid": _c.STATUS_SENT,
        "deferred": _c.STATUS_ERROR,
        "blocked": _c.STATUS_ERROR,
        "unsubscribed": _c.STATUS_REJECTED,
        "error": _c.STATUS_ERROR,
        "loadedByProxy": _c.STATUS_SENT,
    }

    def update_event(self, event):
        if event in self.STATUS:
            self.missive.status = self.STATUS[event]
            self.missive.save()

    def on_webhook(self, request):
        from mighty.models import Missive
        data = json.loads(request.body)
        try:
            self.missive = Missive.objects.get(partner_id=data.get("message-id"))
            self.update_event(data.get("event"))
        except Missive.DoesNotExist:
            pass
        return data

    def check_email(self):
        data = {
            "message_id": self.missive.partner_id
        } if self.missive.partner_id else {
            "tag": self.missive.msg_id
        }
        api_response = self.api_instance.get_email_event_report(**data, email=self.missive.target)
        event = api_response.events[0].event
        self.update_event(event)
        return api_response

    @property
    def api_instance(self):
        if not self.api_instance_cache:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.APIKEY
            self.api_instance_cache = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration))
        return self.api_instance_cache

    def email_attachments(self):
        attachments = []
        if self.missive.attachments:
            logs = []
            for document in self.missive.attachments:
                if setting('MISSIVE_SERVICE', False):
                    attachments.append({
                        "content": base64.b64encode(document.read()).decode('utf-8'),
                        "name": os.path.basename(document.name),
                    })
                logs.append(os.path.basename(document.name))
            self.missive.logs['attachments'] = logs
        return attachments

    def setup_template_params(self, data):
        if data["template_id"] == 1:
            data["params"] = {
                "code": self.missive.context["code"],
                "domain": MightyConfig.domain.upper(),
                "link":  "https://%s" % MightyConfig.domain,
            }

    def forge_email(self, data, attachments):
        data["to"] = [{"email": self.missive.target}]
        data["headers"] = {"charset": "utf-8"}
        if self.reply_email:
            data["reply_to"] = {"email": self.reply_email, "name": self.reply_name}
        if self.missive.sender:
            data["sender"] = {"email": self.missive.sender, "name": self.missive.name}
        if self.missive.subject:
            data["subject"] = self.missive.subject
        if 'template_id' in self.missive.context and self.missive.context["template_id"]:
            data["template_id"] = self.missive.context["template_id"]
            self.setup_template_params(data)
        else:
            if self.missive.html_format:
                data["html_content"] = self.missive.html_format
            if self.missive.txt:
                data["text_content"] = str(self.missive.txt)
        if len(attachments):
            data["attachment"] = attachments

    def send_email(self):
        data = {}
        over_target = setting('MISSIVE_EMAIL', False)
        self.missive.target = over_target if over_target else self.missive.target
        self.logger.info("Email - from : %s, to : %s, reply : %s" % (self.sender_email, self.missive.target, self.reply_email))
        if setting('MISSIVE_SERVICE', False):
            try:
                self.api_instance.smtp_blocked_contacts_email_delete(self.missive.target)
            except Exception:
                pass
            self.missive.msg_id = make_msgid()
            attachments = self.email_attachments()
            self.forge_email(data, attachments)
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**data)
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            self.missive.partner_id = api_response.message_id
        self.missive.to_sent()
        self.missive.save()
        return self.missive.status

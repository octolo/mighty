from django.core.mail.message import make_msgid
from django.conf import settings
from mighty.applications.messenger.backends import MissiveBackend
from mighty.applications.messenger import choices as _c
from mighty.functions import setting
from mighty.apps import MightyConfig
import os, base64, json, requests

class MissiveBackend(MissiveBackend):
    SCW_SECRET_KEY = settings.SCALEWAY_SECRET_ACCESS_KEY_TEM
    SCW_REGION = settings.SCALEWAY_REGION_TEM
    SCW_PROJECT_ID = settings.SCALEWAY_PROJECT_ID_TEM
    SCW_DOMAIN_TEM = settings.SCALEWAY_DOMAIN_TEM
    APIURL = "https://api.scaleway.com/transactional-email/v1alpha1/regions/%s/emails"
    STATUS = {}
    in_error = False


    def update_event(self, event):
        pass

    def on_webhook(self, request):
        pass

    def check_email(self):
        pass

    @property
    def api_url(self): return self.APIURL%self.SCW_REGION

    @property
    def email_data(self):
        data = {
            "subject": self.missive.subject,
            "from": {"email": self.missive.sender, "name":  self.missive.name},
            "project_id": self.SCW_PROJECT_ID,
            "to": [{"email": self.missive.target, "name": self.missive.fullname}],
            "attachments": self.email_attachments,
            #"reply_to": [
            #    {"email": self.reply_email, "name": self.reply_name}
            #],
        }
        if self.missive.html_format: data["html"] = self.missive.html_format
        if self.missive.txt: data["text"] = str(self.missive.txt)
        return data

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

    def send_email(self):
        data = {}
        over_target = setting('MISSIVE_EMAIL', False)
        self.missive.target = over_target if over_target else self.missive.target
        self.logger.info("Email - from: %s, to : %s, reply : %s" % (self.sender_email, self.missive.target, self.reply_email))
        if setting('MISSIVE_SERVICE', False):
            headers = {'X-Auth-Token': self.SCW_SECRET_KEY, "Content-Type": "application/json"}
            response = requests.post(self.api_url, headers=headers, json=self.email_data)
        self.missive.to_sent()
        self.missive.save()
        return self.missive.status

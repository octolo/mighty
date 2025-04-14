import base64
import os

import requests
from django.conf import settings

from mighty.applications.messenger.apps import MessengerConfig as conf
from mighty.applications.messenger.backends import MissiveBackend


class MissiveBackend(MissiveBackend):
    SCW_SECRET_KEY = settings.AWS_SECRET_ACCESS_KEY
    SCW_REGION = settings.AWS_S3_REGION_NAME
    SCW_PROJECT_ID = settings.SCW_PROJECT_ID_TEM
    # SCW_DOMAIN = settings.SCALEWAY_DOMAIN
    APIURL = 'https://api.scaleway.com/transactional-email/v1alpha1/regions/%s/emails'
    STATUS = {}
    in_error = False

    def update_event(self, event):
        pass

    def on_webhook(self, request):
        pass

    def check_email(self):
        pass

    @property
    def api_url(self):
        return self.APIURL % self.SCW_REGION

    @property
    def email_data(self):
        data = {
            'subject': self.missive.subject,
            'from': {'email': self.missive.sender, 'name': self.missive.name},
            'project_id': self.SCW_PROJECT_ID,
            'to': [
                {'email': self.missive.target, 'name': self.missive.fullname}
            ],
            'attachments': self.email_attachments(),
            'additional_headers': [
                {'key': 'Reply-To', 'value': self.reply_email}
            ],
        }
        if self.missive.html_format:
            data['html'] = self.missive.html_format
        if self.missive.txt:
            data['text'] = str(self.missive.txt)
        return data

    def email_attachments(self):
        attachments = []
        if self.missive.attachments:
            logs = []
            for document in self.missive.attachments:
                if getattr(settings, 'MISSIVE_SERVICE', False):
                    attachments.append({
                        'content': base64.b64encode(document.read()).decode(
                            'utf-8'
                        ),
                        'name': os.path.basename(document.name),
                    })
                logs.append(os.path.basename(document.name))
            self.missive.logs['attachments'] = logs
        return attachments

    def send_email(self):
        # FIXME: Cleanup
        self.missive.sender = (
            f'{conf.sender_name}@tem.{os.environ.get("DOMAIN")}'
            if settings.IS_PROD_OR_PREPROD
            else 'contact@tem.dev.octolo.tech'
        )
        over_target = getattr(settings, 'MISSIVE_EMAIL', False)
        self.missive.target = over_target or self.missive.target
        self.logger.info(
            f'Email - from: {self.sender_email}, to : {self.missive.target}, reply : {self.reply_email}'
        )
        if getattr(settings, 'MISSIVE_SERVICE', False):
            headers = {
                'X-Auth-Token': self.SCW_SECRET_KEY,
                'Content-Type': 'application/json',
            }
            requests.post(self.api_url, headers=headers, json=self.email_data)
        self.missive.to_sent()
        self.missive.save()
        return self.missive.status


# EMERGENCY
# ./manage.py redis_var --key emergency_email --value mighty.applications.messenger.backends.email.scaleway

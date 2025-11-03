# https://www.maileva.com/developpeur
# https://secure2.recette.maileva.com/

import json
import os
import tempfile
import threading
import time
from uuid import uuid4

import requests
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.template import Template
from django.utils.text import get_valid_filename

from mighty.applications.messenger import choices as _c
from mighty.applications.messenger.backends import MissiveBackend
from mighty.apps import MightyConfig
from mighty.functions import setting
from mighty.functions.facilities import getattr_recursive
from mighty.models import Missive
import pathlib
import contextlib


MAILEVA_COLOR_FIRST_C4 = 0.73
MAILEVA_COLOR_NEXT_C4 = 0.48
MAILEVA_NB_FIRST_C4 = 0.48
MAILEVA_NB_NEXT_C4 = 0.23
MAILEVA_ARCHIVING_LTE3_FIRST = 0.03
MAILEVA_ARCHIVING_LTE6_FIRST = 0.03
MAILEVA_ARCHIVING_LTE10_FIRST = 0.03
MAILEVA_ARCHIVING_LTE3_NEXT = 0.03
MAILEVA_ARCHIVING_LTE6_NEXT = 0.03
MAILEVA_ARCHIVING_LTE10_NEXT = 0.03

class MissiveBackend(MissiveBackend):
    """ Maileva backend for sending postal missives."""
    has_proofs = True
    resource_type = 'registered_mail/v4/sendings'
    callback_url = MightyConfig.webhook + '/wbh/messenger/postalar/'
    api_sandbox = {  # noqa: RUF012
        'webhook': 'https://api.sandbox.maileva.net/notification_center/v4/subscriptions',
        'auth': 'https://connexion.sandbox.maileva.net/auth/realms/services/protocol/openid-connect/token',
        'sendings': 'https://api.sandbox.maileva.net/registered_mail/v4/sendings',
        'documents': 'https://api.sandbox.maileva.net/registered_mail/v4/sendings/%s/documents',
        'recipients': 'https://api.sandbox.maileva.net/registered_mail/v4/sendings/%s/recipients',
        'submit': 'https://api.sandbox.maileva.net/registered_mail/v4/sendings/%s/submit',
        'cancel': 'https://api.sandbox.maileva.com/registered_mail/v4/sendings/%s',
        'prooflist': 'https://api.sandbox.maileva.net/registered_mail/v4/global_deposit_proofs?sending_id=%s',
        'proof': 'https://api.sandbox.maileva.net/registered_mail/v4/global_deposit_proofs/%s',
        'proofdownload': 'https://api.sandbox.maileva.net/registered_mail/v4%s',
    }
    api_sandbox = {  # noqa: RUF012
        'webhook': 'https://api.maileva.com/notification_center/v4/subscriptions',
        'auth': 'https://connexion.maileva.com/auth/realms/services/protocol/openid-connect/token',
        'sendings': 'https://api.maileva.com/registered_mail/v4/sendings',
        'documents': 'https://api.maileva.com/registered_mail/v4/sendings/%s/documents',
        'recipients': 'https://api.maileva.com/registered_mail/v4/sendings/%s/recipients',
        'submit': 'https://api.maileva.com/registered_mail/v4/sendings/%s/submit',
        'cancel': 'https://api.maileva.com/registered_mail/v4/sendings/%s',
        'prooflist': 'https://api.maileva.com/registered_mail/v4/global_deposit_proofs?sending_id=%s',
        'proof': 'https://api.maileva.com/registered_mail/v4/global_deposit_proofs/%s',
        'proofdownload': 'https://api.maileva.com/registered_mail/v4%s',
    }
    proof_keys = [
        'content_proof_embedded_document',
        'deposit_proof',
        'content_proof',
        'acknowledgement_of_receipt',
    ]
    status_ref = {  # noqa: RUF012
        'PENDING': _c.STATUS_PENDING,
        'ACCEPTED': _c.STATUS_ACCEPTED,
        'PROCESSED': _c.STATUS_PROCESSED,
        'DRAFT': _c.STATUS_ERROR,
        'REJECTED': _c.STATUS_REJECTED,
        'PROCESSED_WITH_ERRORS': _c.STATUS_PROCESSED,
    }
    events = [  # noqa: RUF012
        'ON_STATUS_ACCEPTED',
        'ON_STATUS_REJECTED',
        'ON_STATUS_PROCESSED',
        'ON_DEPOSIT_PROOF_RECEIVED',
    ]
    fields = ['denomination', 'fullname', 'complement', 'address']  # noqa: RUF012
    user_cache = None
    sending_id = None
    access_token = None
    priority = 1
    header_offset = 72
    js_admin = False
    page = 0

    # PRICE
    color_first_c4 = setting('MAILEVA_COLOR_FIRST_C4', MAILEVA_COLOR_FIRST_C4)
    color_next_c4 = setting('MAILEVA_COLOR_NEXT_C4', MAILEVA_COLOR_NEXT_C4)
    nb_first_c4 = setting('MAILEVA_NB_FIRST_C4', MAILEVA_NB_FIRST_C4)
    nb_next_c4 = setting('MAILEVA_NB_NEXT_C4', MAILEVA_NB_NEXT_C4)
    archiving_lte3_first = setting('MAILEVA_ARCHIVING_LTE3_FIRST', MAILEVA_ARCHIVING_LTE3_FIRST)
    archiving_lte6_first = setting('MAILEVA_ARCHIVING_LTE6_FIRST', MAILEVA_ARCHIVING_LTE6_FIRST)
    archiving_lte10_first = setting('MAILEVA_ARCHIVING_LTE10_FIRST', MAILEVA_ARCHIVING_LTE10_FIRST)
    archiving_lte3_next = setting('MAILEVA_ARCHIVING_LTE3_NEXT', MAILEVA_ARCHIVING_LTE3_NEXT)
    archiving_lte6_next = setting('MAILEVA_ARCHIVING_LTE6_NEXT', MAILEVA_ARCHIVING_LTE6_NEXT)
    archiving_lte10_next = setting('MAILEVA_ARCHIVING_LTE10_NEXT', MAILEVA_ARCHIVING_LTE10_NEXT)

    # CONFIG
    color_printing = setting('MAILEVA_COLOR_PRINTING', False)  # noqa: FBT003
    duplex_printing = bool(setting('MAILEVA_DUPLEX_PRINTING', True))  # noqa: FBT003
    optional_address_sheet = bool(setting('MAILEVA_OPTIONAL_ADDRESS_SHEET', True))  # noqa: FBT003
    archiving_duration = setting('MAILEVA_ARCHIVING_DURATION', 0)
    notification_email = setting('MAILEVA_NOTIFICATION', False)  # noqa: FBT003

    # SENDER
    sender_address_line_1 = setting('MAILEVA_SENDER1')
    sender_address_line_2 = setting('MAILEVA_SENDER2')
    sender_address_line_3 = setting('MAILEVA_SENDER3')
    sender_address_line_4 = setting('MAILEVA_SENDER4')
    sender_address_line_5 = setting('MAILEVA_SENDER5')
    sender_address_line_6 = setting('MAILEVA_SENDER6')
    sender_country_code = setting('MAILEVA_SENDERC')

    field_price = 'trace_json.recipients.recipients.0.postage_price'
    field_billed_page = 'trace_json.status.billed_pages_count'
    field_external_reference = 'trace_json.status.reference'
    field_external_status = 'trace_json.recipients.recipients.0.last_main_delivery_status.label'
    field_color = 'trace_json.status.color_printing'
    field_type = 'trace_json.status.envelope_type'
    field_class = 'trace_json.recipients.recipients.0.postage_class'

    def __init__(self, missive, *args, **kwargs):
        """Initialize the Maileva backend with missive and configuration."""
        super().__init__(missive, *args, **kwargs)
        self.color_first_c4 = kwargs.get('color_first_c4', self.color_first_c4)
        self.color_next_c4 = kwargs.get('color_next_c4', self.color_next_c4)
        self.nb_first_c4 = kwargs.get('nb_first_c4', self.nb_first_c4)
        self.nb_next_c4 = kwargs.get('nb_next_c4', self.nb_next_c4)
        self.archiving_lte3_first = kwargs.get(
            'archiving_lte3_first', self.archiving_lte3_first
        )
        self.archiving_lte6_first = kwargs.get(
            'archiving_lte6_first', self.archiving_lte6_first
        )
        self.archiving_lte10_first = kwargs.get(
            'archiving_lte10_first', self.archiving_lte10_first
        )
        self.archiving_lte3_next = kwargs.get(
            'archiving_lte3_next', self.archiving_lte3_next
        )
        self.archiving_lte6_next = kwargs.get(
            'archiving_lte6_next', self.archiving_lte6_next
        )
        self.archiving_lte10_next = kwargs.get(
            'archiving_lte10_next', self.archiving_lte10_next
        )
        self.color_printing = kwargs.get('color_printing', self.color_printing)
        self.duplex_printing = kwargs.get(
            'duplex_printing', self.duplex_printing
        )
        self.optional_address_sheet = kwargs.get(
            'optional_address_sheet', self.optional_address_sheet
        )
        self.archiving_duration = kwargs.get(
            'archiving_duration', self.archiving_duration
        )
        self.notification_email = kwargs.get(
            'notification_email', self.notification_email
        )
        self.sender_address_line_1 = kwargs.get(
            'sender_address_line_1', self.sender_address_line_1
        )
        self.sender_address_line_2 = kwargs.get(
            'sender_address_line_2', self.sender_address_line_2
        )
        self.sender_address_line_3 = kwargs.get(
            'sender_address_line_3', self.sender_address_line_3
        )
        self.sender_address_line_4 = kwargs.get(
            'sender_address_line_4', self.sender_address_line_4
        )
        self.sender_address_line_5 = kwargs.get(
            'sender_address_line_5', self.sender_address_line_5
        )
        self.sender_address_line_6 = kwargs.get(
            'sender_address_line_6', self.sender_address_line_6
        )
        self.sender_country_code = kwargs.get(
            'sender_country_code', self.sender_country_code
        )
        self.notification_treat_undelivered_mail = kwargs.get(
            'notification_treat_undelivered_mail', []
        )

    @property
    def sender_height(self):
        return 145 - self.header_offset

    @property
    def address_block(self):
        sender_style = f'height:{self.sender_height!s}px;'
        target_style = 'height:171px;padding-bottom:35px;'
        sender_content = ''
        target_content = ''
        if self.missive.status == _c.STATUS_FILETEST:
            sender_style += 'background-color:gray;color: white;'
            target_style += 'background-color:blue;color: white;'
            sender_content = 'SENDER'
            target_content = 'TARGET'
        return f"""<div style="{sender_style}">{sender_content}</div><div style="{target_style}">{target_content}</div>"""

    def postal_template(self, context):
        return Template(self.address_block + self.missive.html).render(context)

    @property
    def postal_data(self):
        undelivered = setting('MAILEVA_EMAIL_UNDELIVERED', None)
        undelivered = [undelivered] if undelivered else []
        if self.missive.reply:
            undelivered.append(self.missive.reply)
        base = {
            'name': self.missive.target,
            'custom_id': self.missive.msg_id,
            'custom_data': self.missive.msg_id,
            'color_printing': self.color_printing,
            'duplex_printing': self.duplex_printing,
            'optional_address_sheet': self.optional_address_sheet,
            'archiving_duration': self.archiving_duration,
            'sender_address_line_1': self.sender_address_line_1,
            'sender_address_line_2': self.sender_address_line_2,
            'sender_address_line_3': self.sender_address_line_3,
            'sender_address_line_4': self.sender_address_line_4,
            'sender_address_line_5': self.sender_address_line_5,
            'sender_address_line_6': self.sender_address_line_6,
            'sender_country_code': self.sender_country_code,
            'envelope_windows_type': 'DOUBLE',
        }

        if self.missive.model == _c.MODE_POSTALAR:
            base.update({
                'acknowledgement_of_receipt': True,
                'acknowledgement_of_receipt_scanning': False,
            })

        return base

    @property
    def user_webhook(self):
        if not self.user_cache:
            from oauth2_provider.models import Application

            self.user_cache = Application.objects.get(
                user__email=setting('MAILEVA_OAUTH_EMAIL')
            )
        return self.user_cache

    @property
    def webhook_data(self):
        return {
            'resource_type': self.resource_type,
            'callback_url': self.callback_url,
        }

    @property
    def target_data(self):
        data = {
            'custom_id': self.missive.msg_id,
            'custom_data': self.missive.msg_id,
            'address_line_6': self.missive.city,
            'address_line_5': self.missive.cedex
            or self.missive.cedex_code
            or self.missive.special
            or '',
            'country_code': self.missive.country_code.upper(),
        }
        for i, field in enumerate(self.fields):
            attr = getattr(self.missive, field)
            if attr:
                data['address_line_' + str(i + 1)] = attr[:38]
        return data

    @property
    def api_url(self):
        if not settings.IS_PROD:
            return self.api_sandbox
        return self.api_official

    @property
    def api_headers(self):
        return {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }

    def valid_response(self, response):
        if response.status_code not in {200, 201, 204}:
            self.missive.trace = str(response.content)
            if str(response.status_code).startswith('4'):
                try:
                    if 'code' in response.json():
                        self.missive.code_error = response.json()['code']
                    else:
                        self.missive.code_error = response.json()['error']
                except:
                    self.missive.code_error = 'unknown'
            self.in_error = True
            return False
        return True

    def authentication(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        auth = (setting('MAILEVA_CLIENTID'),setting('MAILEVA_SECRET'))
        data = {
            'grant_type': 'password',
            'username': setting('MAILEVA_USERNAME'),
            'password': setting('MAILEVA_PASSWORD'),
        }
        response = requests.post(self.api_url['auth'], headers=headers, auth=auth, data=data)
        if self.valid_response(response):
            self.access_token = response.json()['access_token']
            return True
        return False

    def create_sending(self):
        response = requests.post(
            self.api_url['sendings'],
            headers=self.api_headers,
            json=self.postal_data,
        )
        self.sending_id = response.json()['id']
        self.missive.partner_id = self.sending_id
        return self.valid_response(response)

    def check_documents(self):
        if self.authentication():
            url = self.api_url['documents'] % self.missive.partner_id
            response = requests.get(url, headers=self.api_headers)
            return response.json()
        return None

    def postal_add_attachment(self, attachment):
        self._logger.info(f'postal_add_attachment {attachment.name}')
        self.priority += 1
        api = self.api_url['documents'] % self.sending_id
        headers = self.api_headers
        doc_name = os.path.basename(attachment.name)
        data = {'priority': self.priority, 'name': doc_name, 'shrink': True}
        files = {
            'document': (doc_name, open(attachment.name, 'rb').read()),
            'metadata': ('metadata', json.dumps(data), 'application/json'),
        }
        response = requests.post(api, headers=headers, files=files)
        self.valid_response(response)
        self.add_log_array('attachments', doc_name)

    def postal_attachments(self):
        if self.missive.attachments:
            for document in self.missive.attachments:
                suffix = get_valid_filename(os.path.basename(str(document)))
                with tempfile.NamedTemporaryFile(
                    suffix=suffix, delete=False
                ) as tmp_pdf:
                    tmp_pdf.write(document.read())
                    self.postal_add_attachment(tmp_pdf)
        return not self.in_error

    def add_recipients(self):
        api = self.api_url['recipients'] % self.sending_id
        response = requests.post(
            api, headers=self.api_headers, json=self.target_data
        )
        return self.valid_response(response)

    def submit(self):
        api = self.api_url['submit'] % self.sending_id
        response = requests.post(api, headers=self.api_headers)
        return self.valid_response(response)

    def enable_webhooks(self):
        for event in self.events:
            wdata = self.webhook_data
            wdata['event_type'] = event
            api = self.api_url['webhook']
            response = requests.post(api, headers=self.api_headers, json=wdata)
            self.valid_response(response)

    def on_webhook(self, request):
        key = request.GET.get('key')
        if key:
            missive = get_object_or_404(Missive, msg_id=key)
        else:
            partner_id = request.POST.get('resource_id')
            missive = get_object_or_404(Missive, partner_id=partner_id)
        missive.check_status()

    def send_postal(self):
        # self.set_price_config()
        self.missive.msg_id = str(uuid4())
        if self.missive.status == _c.STATUS_FILETEST:
            self.postal_base()
        elif self.authentication():
            if not self.in_error:
                self.create_sending()
            if not self.in_error:
                self.add_recipients()
            if not self.in_error:
                self.postal_base()
                self.postal_attachments()
            if not self.in_error and self.submit():
                self.missive.to_sent()
                # self.set_price_info()
                if setting('MAILEVA_WEBHOOK'):
                    self.enable_webhooks()
            else:
                self.missive.to_error()
            getattr(self, f'check_{self.missive.mode.lower()}')()
            return self.missive.status
        return None

    def price_archive(self, page, archive):
        if not archive or not page:
            return 0
        if archive <= 3:
            return self.archiving_lte3_first + (
                self.archiving_lte3_next * (page - 1)
            )
        if archive <= 6:
            return self.archiving_lte6_first + (
                self.archiving_lte6_next * (page - 1)
            )
        if archive <= 10:
            return self.archiving_lte10_first + (
                self.archiving_lte10_next * (page - 1)
            )
        return None

    def price_page(self, count_page, color=False, archive=0):
        price, pnext, _parchive = (0.73, 0.48) if color else (0.48, 0.23)
        if count_page > 1:
            price += pnext * (count_page - 1)
        price += self.price_archive(count_page, archive)
        return price

    def price_config(self):
        return {
            'color_first_c4': self.color_first_c4,
            'color_next_c4': self.color_next_c4,
            'nb_first_c4': self.nb_first_c4,
            'nb_next_c4': self.nb_next_c4,
            'archiving_lte3_first': self.archiving_lte3_first,
            'archiving_lte6_first': self.archiving_lte6_first,
            'archiving_lte10_first': self.archiving_lte10_first,
            'archiving_lte3_next': self.archiving_lte3_next,
            'archiving_lte6_next': self.archiving_lte6_next,
            'archiving_lte10_next': self.archiving_lte10_next,
        }

    def prince_info(self):
        return {
            'count_page': self.count_page,
            'duplex_printing': self.duplex_printing,
            'color_printing': self.color_printing,
            'archiving_duration': self.archiving_duration,
            'optional_address_sheet': self.optional_address_sheet,
        }

    def price(self):
        pages = self.price_info['count_page']
        pages += 1 if self.prince_info['optional_address_sheet'] else 0
        self.price_page(
            count_page=pages,
            color=self.price_info['color_printing'],
            archive=self.prince_info['archiving_duration'],
        )

    def get_status(self):
        if self.authentication():
            url = self.api_url['sendings'] + '/' + self.missive.partner_id
            response = requests.get(url, headers=self.api_headers)
            return response.json()
        return {'status': 'ERROR', 'message': 'Authentication failed'}

    def get_recipients(self):
        if self.authentication():
            url = self.api_url['recipients'] % self.missive.partner_id
            response = requests.get(url, headers=self.api_headers)
            return response.json()
        return {'recipients': []}

    def check_postalar(self):
        rjson_status = self.get_status()
        rjson_recipients = self.get_recipients()
        rjson = {
            'status': rjson_status,
            'recipients': rjson_recipients,
        }
        self.missive.trace = str(rjson)
        status_value = rjson_status.get('status')
        if status_value:
            self.missive.status = self.status_ref.get(status_value, self.missive.status)
        self.missive.save()
        return rjson

    def cancel(self):
        if self.authentication():
            api = self.api_url['cancel'] % self.missive.partner_id
            response = requests.delete(api, headers=self.api_headers)
            if self.valid_response(response):
                self.missive.status = _c.STATUS_CANCELLED
            self.missive.save()

    def get_prooflist(self):
        proofs = self.get_recipients()
        proofs = proofs.get('recipients', [])[0]
        return [kp for kp in self.proof_keys if kp + '_url' in proofs]

    def download_proof(self, proof, http_response=True):
        proofs = self.get_recipients()
        proofs = proofs.get('recipients', [])[0]
        proof_url = proofs.get(proof + '_url', None)

        if not proof:
            return None

        proof_url = self.api_url['proofdownload'] % proof_url
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        resp = requests.get(proof_url, stream=True, headers=self.api_headers)
        resp.raise_for_status()

        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                tmp_file.write(chunk)
        tmp_file.close()

        if not http_response:
            return tmp_file.name

        name = self.missive.fullname
        file = open(tmp_file.name, 'rb')
        date = time.strftime('%Y%m%d_%H%M%S')
        filename = get_valid_filename(f'{name}_{proof}_{date}.pdf')

        print("filename:", filename)
        response = FileResponse(file, as_attachment=True, filename=filename)

        # Supprimer le fichier après un petit délai
        def cleanup(path, f):
            time.sleep(15)  # délai pour laisser le serveur envoyer le fichier
            f.close()
            with contextlib.suppress(FileNotFoundError):
                pathlib.Path(path).unlink()
        threading.Thread(target=cleanup, args=(tmp_file.name, file)).start()

        return response

    def get_price(self):
        return getattr_recursive(self.missive, self.field_price, default='', default_on_error=True)

    def get_billed_page(self):
        return getattr_recursive(self.missive, self.field_billed_page, default='', default_on_error=True)

    def get_external_reference(self):
        return getattr_recursive(self.missive, self.field_external_reference, default='', default_on_error=True)

    def get_external_status(self):
        return getattr_recursive(self.missive, self.field_external_status, default='', default_on_error=True)

    def get_color(self):
        return getattr_recursive(self.missive, self.field_color, default='', default_on_error=True)

    def get_class(self):
        return getattr_recursive(self.missive, self.field_class, default='', default_on_error=True)

    def get_type(self):
        return getattr_recursive(self.missive, self.field_type, default='', default_on_error=True)

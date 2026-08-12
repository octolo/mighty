import base64
import contextlib
import json
import logging
import os

import sib_api_v3_sdk
from django.core.mail.message import make_msgid

from mighty.applications.messenger import choices as _c
from mighty.applications.messenger.backends import MissiveBackend
from mighty.apps import MightyConfig
from mighty.functions import setting

logger = logging.getLogger(__name__)


class MissiveBackend(MissiveBackend):
    APIKEY = setting('SENDINBLUE_KEY', False)
    APIURL = 'https://api.sendinblue.com/v3/smtp/email'
    in_error = False
    api_instance_cache = None

    STATUS = {
        'bounces': _c.STATUS_ERROR,
        'hardBounces': _c.STATUS_ERROR,
        'softBounces': _c.STATUS_ERROR,
        'delivered': _c.STATUS_SENT,
        'spam': _c.STATUS_ERROR,
        'requests': _c.STATUS_PROCESSED,
        'opened': _c.STATUS_OPEN,
        'clicks': _c.STATUS_OPEN,
        'invalid': _c.STATUS_SENT,
        'deferred': _c.STATUS_ERROR,
        'blocked': _c.STATUS_ERROR,
        'unsubscribed': _c.STATUS_REJECTED,
        'error': _c.STATUS_ERROR,
        'loadedByProxy': _c.STATUS_SENT,
    }

    @staticmethod
    def truncate_code_error(reason):
        if not reason:
            return None
        # Missive.code_error is CharField(max_length=255)
        return reason[:255]

    @staticmethod
    def event_to_dict(event):
        if isinstance(event, dict):
            return event
        return {
            'event': getattr(event, 'event', None),
            'message_id': getattr(event, 'message_id', None),
            'email': getattr(event, 'email', None),
            'date': getattr(event, 'date', None),
            'reason': getattr(event, 'reason', None),
            'tag': getattr(event, 'tag', None),
            'subject': getattr(event, 'subject', None),
        }

    def update_event(self, event, events=None):
        changed = False
        if events is not None:
            self.missive.trace = repr(events)
            changed = True
            if event in self.STATUS and self.STATUS[event] == _c.STATUS_ERROR:
                reason = next(
                    (e.get('reason') for e in events if e.get('reason')),
                    None,
                )
                if reason:
                    self.missive.code_error = self.truncate_code_error(reason)
        if event in self.STATUS:
            self.missive.status = self.STATUS[event]
            changed = True
        if changed:
            self.missive.save()

    def on_webhook(self, request):
        from mighty.models import Missive

        data = json.loads(request.body)
        try:
            self.missive = Missive.objects.get(
                partner_id=data.get('message-id')
            )
            self.update_event(data.get('event'))
        except Missive.DoesNotExist:
            pass
        return data

    def check_email(self):
        data = (
            {'message_id': self.missive.partner_id}
            if self.missive.partner_id
            else {'tag': self.missive.msg_id}
        )
        api_response = self.api_instance.get_email_event_report(
            **data, email=self.missive.target
        )
        event = api_response.events[0].event
        self.update_event(event)
        return api_response

    @classmethod
    def sync_email_statuses(
        cls,
        days=90,
        start_date=None,
        end_date=None,
        limit=2500,
        progress=None,
        progress_every=100,
    ):
        """
        Refresh missive statuses from Brevo in a few API calls.

        Fetches the unaggregated event report (no messageId filter), keeps
        events per message id (latest first), then updates matching missives
        (status, trace, code_error) by partner_id.

        ``progress`` is an optional callable(str) for progress messages.
        """
        from mighty.models import Missive

        def report(message):
            if progress:
                progress(message)

        backend = cls(missive=None)
        params = {'limit': limit, 'sort': 'desc'}
        if start_date and end_date:
            params['start_date'] = str(start_date)
            params['end_date'] = str(end_date)
        else:
            params['days'] = days

        report('Fetching Brevo event report…')
        events_by_message_id = {}
        offset = 0
        page = 0
        total_events = 0
        while True:
            page += 1
            report(f'  Brevo page {page} (offset={offset})…')
            api_response = backend.api_instance.get_email_event_report(
                offset=offset, **params
            )
            events = api_response.events or []
            if not events:
                report(f'  Brevo page {page}: empty, stop.')
                break
            total_events += len(events)
            for event in events:
                message_id = event.message_id
                if not message_id:
                    continue
                events_by_message_id.setdefault(message_id, []).append(
                    cls.event_to_dict(event)
                )
            report(
                f'  Brevo page {page}: +{len(events)} events '
                f'({total_events} total, '
                f'{len(events_by_message_id)} message ids)'
            )
            if len(events) < limit:
                break
            offset += limit

        if not events_by_message_id:
            report('No Brevo events in range.')
            return {'events': 0, 'updated': 0}

        missives = Missive.objects.filter(
            partner_id__in=events_by_message_id.keys()
        ).only('id', 'partner_id', 'status', 'trace', 'code_error')
        missive_total = missives.count()
        report(
            f'Updating {missive_total} missive(s) from '
            f'{len(events_by_message_id)} Brevo message(s)…'
        )

        updated = 0
        errors = 0
        processed = 0
        for missive in missives.iterator(chunk_size=500):
            processed += 1
            events = events_by_message_id.get(missive.partner_id) or []
            if not events:
                continue
            event_name = events[0]['event']
            status = cls.STATUS.get(event_name)
            if not status:
                continue
            trace = repr(events)
            reason = next(
                (e.get('reason') for e in events if e.get('reason')),
                None,
            )
            code_error = (
                cls.truncate_code_error(reason)
                if status == _c.STATUS_ERROR
                else None
            )
            fields = []
            if missive.status != status:
                missive.status = status
                fields.append('status')
            if missive.trace != trace:
                missive.trace = trace
                fields.append('trace')
            if code_error and missive.code_error != code_error:
                missive.code_error = code_error
                fields.append('code_error')
            if fields:
                try:
                    missive.save(update_fields=fields)
                    updated += 1
                except Exception as exc:
                    errors += 1
                    logger.warning(
                        'Cannot update missive %s from Brevo sync: %s',
                        missive.id,
                        exc,
                    )
            if processed % progress_every == 0 or processed == missive_total:
                report(
                    f'  progress {processed}/{missive_total} '
                    f'(updated={updated}, errors={errors})'
                )

        report(
            f'Brevo sync finished: {updated} updated, {errors} error(s).'
        )
        return {'events': len(events_by_message_id), 'updated': updated}

    @property
    def api_instance(self):
        if not self.api_instance_cache:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.APIKEY
            self.api_instance_cache = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )
        return self.api_instance_cache

    def email_attachments(self):
        attachments = []
        if self.missive.attachments:
            logs = []
            for document in self.missive.attachments:
                document.seek(0)
                if setting('MISSIVE_SERVICE', False):
                    attachments.append({
                        'content': base64.b64encode(document.read()).decode(
                            'utf-8'
                        ),
                        'name': os.path.basename(document.name),
                    })
                logs.append(os.path.basename(document.name))
            self.missive.logs['attachments'] = logs
        return attachments

    def check_documents(self):
        return []

    def setup_template_params(self, data):
        if data['template_id'] == 1:
            data['params'] = {
                'code': self.missive.context['code'],
                'domain': MightyConfig.domain.upper(),
                'link': f'https://{MightyConfig.domain}',
            }

    def forge_email(self, data, attachments):
        data['to'] = [{'email': self.missive.target}]
        data['headers'] = {'charset': 'utf-8'}
        if self.reply_email:
            data['reply_to'] = {
                'email': self.reply_email,
                'name': self.reply_name,
            }
        if self.missive.sender:
            data['sender'] = {
                'email': self.missive.sender,
                'name': self.missive.name,
            }
        if self.missive.subject:
            data['subject'] = self.missive.subject
        if self.missive.context.get('template_id'):
            data['template_id'] = self.missive.context['template_id']
            self.setup_template_params(data)
        else:
            if self.missive.html_format:
                data['html_content'] = self.missive.html_format
            if self.missive.txt:
                data['text_content'] = str(self.missive.txt)
        if len(attachments):
            data['attachment'] = attachments

    def send_email(self):
        data = {}
        over_target = setting('MISSIVE_EMAIL', False)
        self.missive.target = over_target or self.missive.target
        self.logger.info(
            f'Email - from : {self.sender_email}, to : {self.missive.target}, reply : {self.reply_email}'
        )
        if setting('MISSIVE_SERVICE', False):
            with contextlib.suppress(Exception):
                self.api_instance.smtp_blocked_contacts_email_delete(
                    self.missive.target
                )
            self.missive.msg_id = make_msgid()
            attachments = self.email_attachments()
            self.forge_email(data, attachments)
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**data)
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            self.missive.partner_id = api_response.message_id
        self.missive.to_sent()
        self.missive.save()
        return self.missive.status

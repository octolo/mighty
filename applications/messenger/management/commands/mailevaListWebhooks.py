
import requests

from mighty.functions import setting
from mighty.management import BaseCommand


class Command(BaseCommand):
    api = {
        'auth_sandbox': 'https://connexion.sandbox.maileva.net/auth/realms/services/protocol/openid-connect/token',
        'auth_prod': 'https://connexion.maileva.com/auth/realms/services/protocol/openid-connect/token',
        'list_sandbox': 'https://api.sandbox.maileva.net/notification_center/v2/subscriptions',
        'list_prod': 'https://api.maileva.com/notification_center/v2/subscriptions',
    }
    action = 'list'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--action', default='list')

    def handle(self, *args, **options):
        self.action = options.get('action')
        super().handle(*args, **options)

    @property
    def auth_data(self):
        return {
            'username': setting('MAILEVA_USERNAME'),
            'password': setting('MAILEVA_PASSWORD'),
            'grant_type': 'password',
            'client_id': setting('MAILEVA_CLIENTID'),
            'client_secret': setting('MAILEVA_SECRET'),
        }

    def api_headers(self, access_token):
        return {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + access_token,
        }

    def makeJob(self):
        response = requests.post(self.api['auth_sandbox'], data=self.auth_data)
        access_token = response.json()['access_token']

        list_webhooks = requests.get(self.api['list_sandbox'], headers=self.api_headers(access_token)).json()
        if self.action == 'list':
            print(list_webhooks)
        if self.action == 'remove':
            for wbh in list_webhooks['subscriptions']:
                requests.delete(self.api['list_sandbox'] + '/' + wbh['id'], headers=self.api_headers(access_token))

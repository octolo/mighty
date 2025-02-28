import json
import logging

import requests
from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackExceptionHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.client = WebClient(token=settings.SLACKTOKEN)
        super().__init__(*args, **kwargs)

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.client.chat_postMessage(channel=settings.SLACKCHANNEL, text=log_entry)
        except SlackApiError as e:
            print(f'Error sending message: {e}')


class DiscordExceptionHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.webhook_url = settings.DISCORDWEBHOOK
        super().__init__(*args, **kwargs)

    def emit(self, record):
        log_entry = self.format(record)
        data = {'content': log_entry}
        try:
            response = requests.post(self.webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Error sending message: {e}')

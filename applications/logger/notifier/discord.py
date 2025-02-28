import json

import requests

from mighty.applications.logger.settings import DISCORD_WEBHOOK


class DiscordEventNotifier:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or DISCORD_WEBHOOK

    def send_event(self, event_name, event_data, url=None):
        # Create a message template
        message_template = f'Event: {event_name}\nData: {event_data}'
        if url is not None:
            message_template += f'\nURL: {url}'

        # Format the message with the event name, data, and URL
        message = message_template.format(event_name=event_name, event_data=event_data, url=url)

        # Create the payload for the Discord webhook
        payload = {'content': message}

        try:
        # Send the payload to the Discord webhook
            response = requests.post(self.webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Error sending message: {e}')

# Usage
# notifier = DiscordEventNotifier('your-discord-webhook-url')
# notifier.send_event('Test Event', 'This is some test data', 'http://example.com')

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from mighty.applications.logger.settings import SLACK_CHANNEL, SLACK_TOKEN


class SlackEventNotifier:
    def __init__(self, token=None, channel=None):
        self.client = WebClient(token=token or SLACK_TOKEN)
        self.channel = channel or SLACK_CHANNEL

    def send_event(self, event_name, event_data, url=None, channel=None):
        # Create a message template
        message_template = f'Event: {event_name}\nData: {event_data}'
        if url is not None:
            message_template += f'\nURL: <{url}|Click here>'

        # Format the message with the event name, data, and URL
        message = message_template.format(
            event_name=event_name, event_data=event_data, url=url
        )

        # Send the message to the Slack channel
        try:
            self.client.chat_postMessage(
                channel=channel or self.channel, text=message
            )
        except SlackApiError as e:
            print(f'Error sending message: {e}')


# Usage
# notifier = SlackEventNotifier('your-slack-bot-token')
# notifier.send_event('#your-channel', 'Test Event', 'This is some test data')

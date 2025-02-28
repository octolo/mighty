from django.conf import settings

NOTIFIER_CLASS = settings.get('MIGHTY_NOTIFIER_CLASS', (
    'mighty.applications.logger.notifier.discord.DiscordEventNotifier',
    'mighty.applications.logger.notifier.slack.SlackEventNotifier'
))

DISCORD_WEBHOOK = settings.get('MIGHTY_DISCORD_WEBHOOK')
SLACK_TOKEN = settings.get('MIGHTY_SLACK_TOKEN')
SLACK_CHANNEL = settings.get('MIGHTY_SLACK_CHANNEL')

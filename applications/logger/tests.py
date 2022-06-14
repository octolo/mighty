from django.test import SimpleTestCase
import logging

# Create your tests here.
class DiscordTestCase(SimpleTestCase):
    #def test_logger(self):
    #    logger = logging.getLogger(__name__)
    #    logger.info("test logger - level: info")
    #    logger.debug("test logger - level: debug")
    #    logger.error("test logger - level: error")

    def test_channels(self):
        from django.conf import settings
        from mighty.applications.logger.notify.discord import DiscordLogger
        HOOKS = settings.DISCORD_HOOK
        for hook,url in HOOKS.items():
            discord = DiscordLogger(lvl=hook)
            discord.send_msg({
                "content": hook,
                "embeds": [{
                    "title": hook,
                    "description": "test hook",
                }]
            })

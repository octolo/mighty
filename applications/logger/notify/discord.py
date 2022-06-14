from mighty.applications.logger.notify import NotifyBackend
from mighty.applications.messenger import notify_discord

class DiscordLogger(NotifyBackend):
    @property
    def text_data_help(self):
        base = [{
            "title": self.msg,
            "description": "\n".join([":warning: "+data for data in self.help_data])
        }]
        return base

    @property
    def discord_msg_error(self):
        return {
			"content": self.msg,
			"embeds": self.text_data_help,
		}

    def send_msg_error(self):
        self.send_msg(self.discord_msg_error)

    def send_msg(self, msg, blocks=None):
        notify_discord(self.level, **msg)
from mighty.applications.logger.notify import NotifyBackend
from mighty.applications.messenger import notify_discord

class DiscordLogger(NotifyBackend):
    @property
    def slack_self(self):
        pass

    @property
    def text_data_help(self):
        base = [{
            "title": self.msg,
            "description": self.exc_text
        },
        {
            "title": "help",
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
        notify_discord("alerts", **self.discord_msg_error)

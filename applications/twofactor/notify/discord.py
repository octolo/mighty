from mighty.applications.user.notify import NotifyBackend
from mighty.applications.messenger import notify_discord

class DiscordTwoFactor(NotifyBackend):
    def __init__(self, twofactor):
        self.twofactor = twofactor
        self.user = twofactor.user

    @property
    def discord_self(self):
        return "%s, %s (%s)" % (self.user.fullname, self.twofactor.email_or_phone, self.twofactor.code)

    @property
    def date_send(self):
        return self.twofactor.date_update if self.twofactor.date_update else self.twofactor.date_create

    @property
    def discord_msg_creation(self):
        return {
        "content": "New code send : %s" % self.date_send.strftime('%Y-%m-%d %H:%M'),
        "embeds": [{
            "title": ":red_circle: New code send : %s" % self.date_send.strftime('%Y-%m-%d %H:%M'),
            "description": "[%s :link:](%s)" % (self.discord_self, self.url_domain(self.twofactor.admin_change_url))
        }]}

    def send_msg_create(self):
        notify_discord("notifications", **self.discord_msg_creation)

    @property
    def discord_msg_connection(self):
        return {
			"content": "New connexion : %s" % self.date_send.strftime('%Y-%m-%d %H:%M'),
			"embeds": [{
				"title": ":green_circle: New connexion : %s" % self.date_send.strftime('%Y-%m-%d %H:%M'),
				"description": "[%s :link:](%s)" % (self.discord_self, self.url_domain(self.twofactor.admin_change_url))
			}]
		}

    def send_msg_connection(self):
        notify_discord("notifications", **self.discord_msg_connection)
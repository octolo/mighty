from mighty.applications.logger.notify.discord import DiscordLogger

class DiscordTwoFactor(DiscordLogger):
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
        "content": "Code : %s - %s" % (self.date_send.strftime('%Y-%m-%d %H:%M'), self.user.fullname),
        "embeds": [{
            "title": ":red_circle: Code : %s - %s" % (self.date_send.strftime('%Y-%m-%d %H:%M'), self.user.fullname),
            "description": "[%s :link:](%s)" % (self.discord_self, self.url_domain(self.twofactor.admin_change_url))
        }]}

    def send_msg_create(self):
        self.send_msg(self.discord_msg_creation)

    @property
    def discord_msg_connection(self):
        return {
			"content": "Connexion : %s - %s" % (self.date_send.strftime('%Y-%m-%d %H:%M'), self.user.fullname),
			"embeds": [{
				"title": ":green_circle: Connexion : %s - %s" % (self.date_send.strftime('%Y-%m-%d %H:%M'), self.user.fullname),
				"description": "[%s :link:](%s)" % (self.discord_self, self.url_domain(self.twofactor.admin_change_url))
			}]
		}

    def send_msg_connection(self):
        self.send_msg(self.discord_msg_connection)

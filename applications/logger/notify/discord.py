from mighty.applications.logger.notify import NotifyBackend
from mighty.applications.messenger import notify_discord


class DiscordLogger(NotifyBackend):
    @property
    def link_admin(self):
        if self.dblog:
            return '[%s :link:](access error)' % self.url_domain(self.dblog.admin_change_url)

    @property
    def text_data_help(self):
        return [{
            'title': self.msg,
            'description': '\n'.join([':warning: ' + data for data in self.help_data] + [self.link_admin])
        }]

    @property
    def discord_msg_error(self):
        data = {
			'content': self.msg,
			'embeds': self.text_data_help,
		}

        return data

    def send_msg_error(self):
        self.send_msg(self.discord_msg_error)

    def send_msg(self, msg, blocks=None):
        notify_discord(self.level, **msg)

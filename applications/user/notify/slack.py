from mighty.applications.user.notify import NotifyBackend
from mighty.applications.messenger import notify_slack

class SlackUser(NotifyBackend):
    @property
    def slack_self(self):
        base = self.user.fullname
        if self.user.email or self.user.phone:
            base += " - " + self.user.email if self.user.email else self.user.phone
        return base

    @property
    def slack_msg_creation(self):
        return [{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": ":baby: New user on the platform : %s" % self.user.date_create.strftime('%Y-%m-%d %H:%M'),
				"emoji": True
		}},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "<%s| %s :link:>" % (self.url_domain(self.user.admin_change_url), self.slack_self)
		}},
		{ "type": "divider" }]

    def send_msg_create(self):
        text = "New user on the platform : %s" % self.user.date_create.strftime('%Y-%m-%d %H:%M')
        notify_slack("notifications", text=text, blocks=self.slack_msg_creation)

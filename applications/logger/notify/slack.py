from mighty.applications.logger.notify import NotifyBackend
from mighty.applications.messenger import notify_slack

class SlackLogger(NotifyBackend):
    @property
    def slack_self(self):
        pass

    @property
    def text_data_help(self):
        return [{
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": ":warning: "+data,
                "emoji": True
            }
        } for data in self.help_data]

    @property
    def slack_msg_error(self):
        return [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": ":exclamation: %s" % self.msg,
                "emoji": True
            }
        },
        { "type": "divider" },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": self.exc_text,
                "emoji": True
            }
        },
        { "type": "divider" }]

    def send_msg_error(self):
        slack_hook = self.setting("SLACK_HOOK")
        notify_slack("alerts", text=self.msg, blocks=self.slack_msg_error)

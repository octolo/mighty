from mighty.applications.logger.notify.slack import SlackLogger


class SlackTwoFactor(SlackLogger):
    def __init__(self, twofactor):
        self.twofactor = twofactor
        self.user = twofactor.user

    @property
    def slack_self(self):
        return f'{self.user.fullname}, {self.twofactor.email_or_phone} ({self.twofactor.code})'

    @property
    def date_send(self):
        return self.twofactor.date_update or self.twofactor.date_create

    @property
    def slack_msg_creation(self):
        return [
            {
                'type': 'section',
                'text': {
                    'type': 'plain_text',
                    'text': ':red_circle: Code : {} - {}'.format(
                        self.date_send.strftime('%Y-%m-%d %H:%M'),
                        self.user.fullname,
                    ),
                    'emoji': True,
                },
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'<{self.url_domain(self.twofactor.admin_change_url)}| {self.slack_self} :link:>',
                },
            },
            {'type': 'divider'},
        ]

    def send_msg_create(self):
        msg = 'New code send : {}'.format(
            self.date_send.strftime('%Y-%m-%d %H:%M')
        )
        self.send_msg(msg, self.slack_msg_creation)

    @property
    def slack_msg_connection(self):
        return [
            {
                'type': 'section',
                'text': {
                    'type': 'plain_text',
                    'text': ':large_green_circle: Connexion : {} - {}'.format(
                        self.date_send.strftime('%Y-%m-%d %H:%M'),
                        self.user.fullname,
                    ),
                    'emoji': True,
                },
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'<{self.url_domain(self.twofactor.admin_change_url)}| {self.slack_self} :link:>',
                },
            },
            {'type': 'divider'},
        ]

    def send_msg_connection(self):
        msg = 'New connexion : {}'.format(
            self.date_send.strftime('%Y-%m-%d %H:%M')
        )
        self.send_msg(msg, self.slack_msg_connection)

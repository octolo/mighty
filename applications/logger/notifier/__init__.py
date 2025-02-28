from mighty.applications.logger import settings


class GlobalNotifier:
    def __init__(self, notifiers=None):
        self.notifiers = notifiers or settings.NOTIFIER_CLASS

    def send_event(self, event_name, event_data, url=None):
        for notifier in self.notifiers:
            notifier.send_event(event_name, event_data, url)


global_notifier = GlobalNotifier()
# global_notifier.send_event('Test Event', 'This is some test data', 'http://example.com')

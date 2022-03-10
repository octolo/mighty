from mighty.backend import Backend

class NotifyBackend(Backend):
    user = None

    def __init__(self, user):
        self.user = user

    def send_msg_create(self):
        raise NotImplementedError("Subclasses should implement send_msg_create()")
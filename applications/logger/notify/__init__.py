from mighty.backend import Backend
from mighty.applications.logger.apps import LoggerConfig as conf

class NotifyBackend(Backend):
    record = None
    msg = None
    lvl = "info"
    data_ok = (
        "exc_text",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "stack_info",
        "lineno",
        "funcName",
        "status_code",
        "request",
    )

    @property
    def retrieve_ip(self):
        x_forwarded_for = self.record.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.record.request.META.get('REMOTE_ADDR', "NOT FOUND")


    @property
    def retrieve_agent(self):
        return self.record.request.META.get('HTTP_USER_AGENT', "NOT FOUND")

    @property
    def exc_text(self):
        if hasattr(self.record, "exc_text"):
            exc_text = getattr(self.record, "exc_text")
        return "No exc text" if exc_text in ("None", None, False, "") else exc_text

    @property
    def help_data(self):
        list_data = []
        for data in self.data_ok:
            if hasattr(self.record, data):
                list_data.append("%s: %s" % (data, getattr(self.record, data)))
        if hasattr(self.record, "request"):
            list_data += ('ip: ' + self.retrieve_ip, 'user_agent: ' + self.retrieve_agent)
            list_data += (
                'post: '+str(self.record.request.POST), 
                'get: '+str(self.record.request.GET),
            )
            if hasattr(self.record.request, "data"):
                list_data += ('data: '+str(self.record.request.data),)
        return list_data

    def __init__(self, *args, **kwargs):
        self.record = kwargs.get("record")
        self.lvl = kwargs.get("lvl", "info")

    @property
    def level(self):
        return self.record.levelname.lower() if self.record else self.lvl

    @property
    def msg(self):
        if hasattr(self.record, "message"):
            return self.record.message
        elif hasattr(self.record, "args") and len(self.record.args):
            return self.record.msg % self.record.args
        return self.record.msg

    def send(self):
        self.send_msg(self.msg)

    def send_error(self):
        if self.record.levelno >= 30:
            self.send_msg_error()

    def send_msg(self, msg, blocks=None):
        raise NotImplementedError("Subclasses should implement send_msg(msg)")

    def send_msg_error(self):
        raise NotImplementedError("Subclasses should implement send_msg_error()")

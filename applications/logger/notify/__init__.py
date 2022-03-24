from mighty.backend import Backend
from mighty.applications.logger.apps import LoggerConfig as conf

class NotifyBackend(Backend):
    record = None
    msg = None
    data_ok = (
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
    def exc_text(self):
        print(self.record.__dict__)
        if hasattr(self.record, "exc_text"):
            exc_text = getattr(self.record, "exc_text")
        return "No exc text" if exc_text in ("None", None, False, "") else exc_text

    @property
    def help_data(self):
        list_data = []
        for data in self.data_ok:
            if hasattr(self.record, data):
                list_data.append("%s: %s" % (data, getattr(self.record, data)))
        return list_data

    def __init__(self, record):
        self.record = record

    @property
    def msg(self):
        if hasattr(self.record, "message"):
            return self.record.message
        elif hasattr(self.record, "args") and len(self.record.args):
            return self.record.msg % self.record.args
        return self.record.msg

    def send_error(self):
        if self.record.levelno >= 30:
            self.send_msg_error()

    def send_msg_error(self):
        raise NotImplementedError("Subclasses should implement send_msg_error()")
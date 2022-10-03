from mighty.applications.logger import EnableLogger

class TaskBackend(EnableLogger):
    def __init__(self, ct, pk, task, *args, **kwargs):
        self.ct = ct
        self.pk = pk
        self.task = task

    def start(self):
        raise NotImplementedError("Subclasses should implement start()")
    
    def cancel(self):
        raise NotImplementedError("Subclasses should implement cancel()")
    
    def end(self):
        raise NotImplementedError("Subclasses should implement end()")
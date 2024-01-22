from django.core.management.base import CommandError
from mighty.management import ModelBaseCommand
from mighty.models import RegisterTaskSubscription

class Command(ModelBaseCommand):
    tasks = "*"
    action = "start"
    model = RegisterTaskSubscription
    action_associated = {
        "start": "start_task",
    }

    def add_arguments(self, parser):
        parser.add_argument('--tasks', default=self.tasks)
        parser.add_argument('--action', default=self.action)
        super().add_arguments(parser)

    def handle(self, *args, **options):
        self.tasks = options.get('tasks')
        self.action = options.get('action')
        super().handle(*args, **options)

    def on_object(self, obj):
        for action in self.action.split(" "):
            getattr(obj, self.action_associated.get(action))()

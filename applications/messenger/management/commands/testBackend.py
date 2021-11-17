from mighty.management import BaseCommand
from mighty.models import Missive
from mighty.applications.messenger.apps import MessengerConfig
from mighty.functions import get_backends
import sys, re

class Command(BaseCommand):
    cache_missive = None
    backend_path = None
    target = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--backend_path", default=MessengerConfig.missive_backends)
        parser.add_argument("--target", default="test@mighty-py.com")

    def handle(self, *args, **options):
        self.backend_path = options.get('backend_path')
        self.target = options.get('target')
        super().handle(*args, **options)

    @property
    def backend(self):
        return get_backends([self.backend_path], return_tuples=True, path_extend='.MissiveBackend', missive=self.fakeMissive)[0][0]

    @property
    def fakeMissive(self):
        if not self.cache_missive:
            self.cache_missive = Missive(
                target=self.target,
                backend=self.backend_path,
            )
        return self.cache_missive
       
    def do(self):
        print(self.backend_path)
        print(self.cache_missive)
        print(self.backend)
        self.backend.testBackend()
        
        
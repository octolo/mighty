from mighty.management import BaseCommand
from mighty.models import Missive
import sys, re

class Command(BaseCommand):
    mail = None
    msgid = None

    def makeJob(self):
        self.mail = "\n".join(sys.stdin)
        self.get_msgid()

    def get_msgid(self):
        match = re.findall(r'Message-Id: (.*)$', self.mail, re.MULTILINE)
        if len(match):
            self.msgid = match[-1]
            self.send_status()

    def send_status(self):
        try:
            missive = Missive.objects.get(msg_id=self.msgid)
            missive.trace = self.mail
            missive.to_error()
            missive.save()
        except Missive.DoesNotExist:
            pass
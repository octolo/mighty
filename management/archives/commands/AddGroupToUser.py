from mighty.management.commands.CleanModel import Command
from django.contrib.auth.models import Group

class Command(Command):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--group', required=True)

    def do(self, options):
        group = options.get('group')
        try:
            self.group = Group.objects.get(name=group)
            super().do(options)
        except Group.DoesNotExist:
            self.error.add('error', 'This group does not exist "%s"' % group)

    def do_update(self, obj):
        try:
            obj.groups.get(name=self.group)
        except Group.DoesNotExist:
            if self.boolean_input('Add to %s' % obj):
                obj.groups.add(self.group)
                self.logger.info('Group add')



    
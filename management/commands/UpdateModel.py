from mighty.management import BaseCommand

class UpdateModel(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)

    def get_queryset(self):
        if self.pk:
            pk = self.pk.split(',')
            return self.model.objects.filter(**{pk[0]: pk[1]})
        return self.model.objects.all()

    def do(self, options):
        query = self.get_queryset()
        self.total_rows = query.count()
        for obj in query:
            self.current_row+=1
            if self.pbar: self.progressBar(self.current_row, self.total_rows)
            else: self.logger.info('Update object %s/%s "%s"' % (self.current_row, self.total_rows, str(obj)))
            self.alerts = {}
            self.do_update(obj)

    def do_update(self, obj):
        pass
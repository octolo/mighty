from mighty.management.commands.CreateOrUpdateModelFromCSV import Command
from mighty.models import Nationality


class Command(Command):
    fields = {'country': 'Country', 'alpha2': 'Alpha2', 'alpha3': 'Alpha3', 'numeric': 'Numeric', 'numbering': 'Numbering'}

    def on_row(self, row):
        self.prefix_bar = self.reverse['country']
        self.current_info = '{} ({})'.format(row[self.reverse['country']], row[self.reverse['alpha3']])
        obj, _create = Nationality.objects.get_or_create(country=row[self.reverse['country']])
        obj.alpha2 = row[self.reverse['alpha2']]
        obj.alpha3 = row[self.reverse['alpha3']]
        obj.numeric = row[self.reverse['numeric']]
        if row[self.reverse['numbering']]:
            obj.numbering = row[self.reverse['numbering']]
        # img = '%s/flags/%s.png' % (conf.directory, row[self.reverse['alpha2']].lower())
        # if obj.image and os.path.isfile(obj.image.path):
        #     os.remove(obj.image.path)
        #     obj.image = None
        # if os.path.isfile(img):
        #     f = open(img, "rb")
        #     flag = File(f)
        #     obj.image.save(img, flag, save=True)
        obj.save()

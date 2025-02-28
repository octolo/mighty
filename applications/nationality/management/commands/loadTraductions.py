from mighty.management import CSVModelCommand
from mighty.models import TranslateDict


class Command(CSVModelCommand):
    curr_translator = None

    def get_dict_filter(self, path):
        try:
            cf = path.split('.')[0]
            if self.curr_translator is None or self.curr_translator.translator.name != cf:
                if self.curr_translator:
                    self.curr_translator.save()
                self.curr_translator = TranslateDict.objects.get(translator__name=cf)
            return True
        except TranslateDict.DoesNotExist:
            pass
        return False

    def change_trad(self, row):
        trad_path = row['path'].split('.')[1:]
        trad_en = row['new']
        if len(trad_path) == 1:
            self.curr_translator.translates[trad_path[0]] = trad_en
        elif len(trad_path) == 2:
            if trad_path[0] not in self.curr_translator.translates:
                self.curr_translator.translates[trad_path[0]] = {}
            self.curr_translator.translates[trad_path[0]][trad_path[1]] = trad_en
        elif len(trad_path) == 3:
            if trad_path[0] not in self.curr_translator.translates:
                self.curr_translator.translates[trad_path[0]] = {}
            if trad_path[1] not in self.curr_translator.translates[trad_path[0]]:
                self.curr_translator.translates[trad_path[0]][trad_path[1]] = {}
            self.curr_translator.translates[trad_path[0]][trad_path[1]][trad_path[2]] = trad_en
        elif len(trad_path) == 4:
            if trad_path[0] not in self.curr_translator.translates:
                self.curr_translator.translates[trad_path[0]] = {}
            if trad_path[1] not in self.curr_translator.translates[trad_path[0]]:
                self.curr_translator.translates[trad_path[0]][trad_path[1]] = {}
            if trad_path[2] not in self.curr_translator.translates[trad_path[0]][trad_path[1]]:
                self.curr_translator.translates[trad_path[0]][trad_path[1]][trad_path[2]] = {}
            self.curr_translator.translates[trad_path[0]][trad_path[1]][trad_path[2]][trad_path[3]] = trad_en

    def after_job(self):
        self.curr_translator.save()

    def on_row(self, row):
        if row['path']:
            if self.get_dict_filter(row['path']):
                self.change_trad(row)

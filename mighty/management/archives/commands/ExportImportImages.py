from django.core.management.base import CommandError
from django.utils.text import get_valid_filename
from django.core.files import File
from mighty.management import BaseCommand
from mighty.models.abstracts import IMAGE_DEFAULT

import re, os

class Command(BaseCommand):
    excludes = [IMAGE_DEFAULT, ]

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--directory', required=True)
        parser.add_argument('--mode', default="export")


    def do(self, options):
        self.directory = options.get("directory")
        self.mode = options.get("mode")

        if self.mode == "export" and not os.path.isdir(self.directory):
            os.mkdir(self.directory)
            self.logger.info('Directory created: %s' % self.directory)
        elif self.mode == "import" and os.path.isdir(self.directory):
            files = {os.path.splitext(get_valid_filename(f))[0].upper(): f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))}
            self.logger.info('Directory found: %s' % self.directory)
        else:
            raise CommandError('Please check mode (%s) or directory (%s)' % (self.mode, self.directory))

        self.totalrows = self.model.objects.all().count()
        self.inf = 0
        for obj in self.model.objects.all():
            self.current_row+=1
            if self.pbar:
                self.progressBar(self.current_row, self.totalrows)
            else:
                self.logger.info('Update object %s/%s "%s"' % (self.current_row, self.totalrows, obj.display))

            if self.mode == "export" and obj.valid_imagename not in self.excludes:
                self.export_image(obj)
            else:
                self.import_image(obj, files)
        print(self.inf)

    def import_image(self, obj, files):
        found = 0
        sfile = get_valid_filename(obj)
        if sfile in files:
            ffile = files[sfile]
        elif sfile.split("_")[0] in files:
            ffile = files[sfile.split("_")[0]]
        elif "".join(sfile.split("_")) in files:
            ffile = files["".join(sfile.split("_"))]
        else:
            found = 1
            splitfile = re.split(r"[, \-!?:_]+", sfile)
            for sf in splitfile:
                if len(sf) > 3:
                    for f in files :
                        if sf in f or self.similar_text(sf, f) > 80:
                            ffile = files[f]
                            found = 0
                            break
        
        if found:
            self.error.add('Logo', 'not found for: %s' % sfile)
            self.inf += found
        else:
            tfile = File(open("%s%s" % (self.directory, ffile), 'rb'))
            obj.image.save(ffile, tfile)
            

    def export_image(self, obj):
        original = os.getcwd() + obj.image_url
        copy = os.getcwd() + "/%s/%s%s" % (self.directory, get_valid_filename(obj), obj.image_extension)
        os.system('cp %s %s' % (original, copy))
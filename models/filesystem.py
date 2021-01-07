"""
Model class
Add [file, name, mimetype] field at the model

(file_url) return the url file static/media
(download_url) return the download url
(pdf_url) get the pdf in a viewer
(get_mime_type) return the mime type
(image_html) return the html tag <img>
(file_name) return the file name
(valid_file_name) get a valid name for filesystem
(file_extension) return the extension
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils.text import get_valid_filename

from mighty.apps import MightyConfig as conf
from mighty.functions import pretty_size_long, pretty_size_short

from sys import getsizeof
import logging, json

logger = logging.getLogger(__name__)
userModel = get_user_model()
DIRECTION = ((0, 'DIRECTORY'),(1, 'DOCUMENT'),(2, 'FILE'))
FILETYPE = ['d', '-', '-']

class FileSystem(models.Model):
    db_size = models.BigIntegerField(blank=True, null=True)
    direction = models.PositiveSmallIntegerField(choices=DIRECTION, default=2)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey(userModel, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        abstract = True

    def calcul_db_size(self, *args, **kwargs):
        excludes = kwargs.get('excludes', [])
        fltr = kwargs.get('fltr', {})
        size = []
        for key,type_ in self.concrete_fields(excludes).items():
            data = getattr(self, '%s_id' % key) if type_ == 'ForeignKey' else getattr(self, key)
            size.append(getsizeof(data))
        for key,type_ in self.many_fields(excludes).items():
            size += [getsizeof(key) for key,obj in getattr(self, key).in_bulk(**fltr).items()]
        return sum(size) if size else None

    def save(self, *args, **kwargs):
        need_post_create = False if not self.pk else True
        #if self.pk: 
        #    self.db_size = self.calcul_db_size()
        #    self.init_ct()
        #    self.init_owner()
        super().save(*args, **kwargs)

    def post_create(self, *args, **kwargs):
        self.save()

    @property
    def file_type(self):
        return FILETYPE[self.direction]

    @property
    def file_extension(self):
        return '.'+self.__class__.__name__.lower()

    @property
    def file_name(self):
        return get_valid_filename(str(self)+self.file_extension)

    @property
    def inode(self):
        return '%s.%s' % (str(self.content_type.id), str(self.pk))

    @property
    def number_of_links(self):
        return

    def init_ct(self):
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self)

    def init_owner(self):
        if not self.owner and (self.create_by or self.update_by):
            userid, username = getattr(self, 'create_by', self.update_by).split('.')
            try:
                self.owner = userModel.objects.get(id=userid)
            except userModel.DoesNotExist:
                pass

    def biggest_name_value(self, *args, **kwargs):
        excludes = kwargs.get('excludes', [])
        oneline  = kwargs.get('oneline', None)
        manyline = kwargs.get('manyline', None)
        if not oneline and not manyline:
            oneline, manyline = self.data_for_file(excludes)
        biggest_name = biggest_value = ''
        for name,value in oneline.items():
            biggest_name = name if len(name) > len(biggest_name) else biggest_name
            biggest_value = value if len(value) > len(biggest_value) else biggest_value
        return biggest_name, biggest_value

    def data_for_file(self, excludes):
        oneline = {
            self.field_config(key).verbose_name.upper(): str(getattr(self, key))
            for key,type_ in self.concrete_fields(excludes).items()
        }
        manyline = {
            self.field_config(key).verbose_name.upper(): [str(data) for data in getattr(self, key).all()]
            for key,type_ in self.many_fields(excludes).items()
        }
        return oneline, manyline

    def file_format(self, *args, **kwargs):
        excludes = kwargs.get('excludes', [])
        return getattr(self, 'file_%s' % kwargs.get('fileformat', 'txt'))(excludes)

    def file_txt(self, excludes):
        oneline, manyline = self.data_for_file(excludes)
        line = []
        biggest_name, biggest_value = self.biggest_name_value(oneline=oneline, manyline=manyline, excludes=excludes)
        size_name = len(biggest_name)
        size_value = len(biggest_value)
        space_name = ' ' * size_name
        space_value = ' ' * size_value
        minus_name = '-' * size_name
        minus_value = '-' * size_value
        line_template = conf.FileSystem.line_template
        for name,value in oneline.items():
            space = ' ' * (size_name-len(name))
            tpl = line_template % ({'space': space, 'label': name, 'data': value})
            line.append(tpl)
        for name,value in manyline.items():
            space = ' ' * (size_name-len(name))
            line.append(line_template % ({'space': space, 'label': name, 'data': minus_value }))
            line.append('\n'.join([space_name+'  - '+str(d) for d in value]) if value else '')
        return '\n'.join(line)

    def file_json(self, excludes):
        oneline, manyline = self.data_for_file(excludes)
        return json.dumps({'unique': oneline, 'multiple': manyline})

    def db_size_long(self, unit=None):
        return pretty_size_long(self.db_size, unit) if self.db_size else None

    def db_size_short(self, unit=None):
        return pretty_size_short(self.db_size, unit) if self.db_size else None

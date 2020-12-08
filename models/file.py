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
from django.utils.text import get_valid_filename
from django.utils.html import format_html
from mighty.functions import file_directory_path
from mighty.fields import JSONField
import os, magic

import logging
logger = logging.getLogger(__name__)

class File(models.Model):
    file = models.FileField(upload_to=file_directory_path, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    filemimetype = models.CharField(max_length=255, blank=True, null=True, editable=False)
    charset = models.CharField(max_length=255, blank=True, null=True, editable=False)
    extracontenttype = JSONField(blank=True, null=True)
    size = models.BigIntegerField(default=0, editable=False)

    class Meta:
        abstract = True

    @property
    def file_url(self): return self.file.url

    @property
    def file_name(self):
        return self.filename if self.filename else os.path.basename(self.file.name)

    @property
    def valid_file_name(self):
        logger.warning('test: %s' % self.file)
        return get_valid_filename(self.file.name)

    @property
    def file_extension(self): return os.path.splitext(self.file_name)[-1]

    @property
    def download_url(self):
        if hastattr(self, 'uid'):
            return self.get_url('download', arguments={'uid': self.uid})
        return self.get_url('download', arguments={'pk': self.pk})

    @property
    def pdf_url(self):
        if hastattr(self, 'uid'):
            return self.get_url('pdf', arguments={'uid': self.uid})
        return self.get_url('pdf', arguments={'pk': self.pk})

    def save(self, *args, **kwargs):
        if self.file._file:
            self.filemimetype = self.file._file.content_type
            self.size = self.file._file.size
            self.charset = self.file._file.charset
            self.extracontenttype = self.file._file.content_type_extra
        super(File, self).save(*args, **kwargs)


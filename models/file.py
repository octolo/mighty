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
import os, mimetypes

class File(models.Model):
    file = models.FileField(upload_to=file_directory_path, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    filemimetype = models.CharField(max_length=255, blank=True, null=True)
    size = models.BigIntegerField(default=0)

    class Meta:
        abstract = True

    @property
    def file_url(self): return self.file.url
    @property
    def get_mime_type(self): return mimetypes.guess_type(self.file.name)[0]
    @property
    def image_html(self): return format_html('<a href="%s" title="%s">' % (self.file.url, self.file_name))
    @property
    def file_name(self): return self.filename if self.filename else os.path.basename(self.file.name)
    @property
    def valid_file_name(self): return get_valid_filename(self.file_name)
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

    @property
    def retrieve_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size

    def save(self, *args, **kwargs):
        if not self.filename : self.filename = self.valid_file_name
        self.size = self.retrieve_size
        self.filemimetype = self.get_mime_type
        super().save(*args, **kwargs)

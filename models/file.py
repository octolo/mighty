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
from django.http import FileResponse
from django.core.exceptions import  PermissionDenied
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.module_loading import import_string

from mighty.functions import file_directory_path, pretty_size_long, pretty_size_short
from mighty.thumbnail import Thumbnail
from mighty.fields import JSONField

import os, magic, logging, requests, tempfile, hashlib
logger = logging.getLogger(__name__)

class File(models.Model):
    auto_complete_fields = [
        "filemimetype",
        "size",
        "charset",
        "extracontenttype",
        "filename",
    ]

    readers = {
        "application/pdf": "mighty.readers.pdf.ReaderPDF",
        ".pdf": "mighty.readers.pdf.ReaderPDF",
    }

    file = models.FileField(upload_to=file_directory_path, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    filemimetype = models.CharField(max_length=255, blank=True, null=True, editable=False)
    charset = models.CharField(max_length=255, blank=True, null=True, editable=False)
    extracontenttype = JSONField(blank=True, null=True)
    metadata = JSONField(blank=True, null=True)
    size = models.BigIntegerField(default=0, editable=False)
    client_date = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    object_id = models.PositiveBigIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    thumbnail = models.TextField(null=True, blank=True)
    hashid = models.CharField(max_length=40, db_index=True, blank=True, null=True)

    # CONFIG
    enable_hashid = False
    enable_thumbnail = False
    proxy_cloud_streaming = False
    chunk_size = 1024
    model_activate_file = True
    local_available = True
    tmp_file = None

    class Meta:
        abstract = True

    @property
    def cloud_file(self):
        cloud_file = requests.get(self.file.url, stream=True)
        cloud_file.raise_for_status()
        status_code = str(cloud_file.status_code)[0]
        if status_code == "2" or status_code == "3":
            #with tempfile.NamedTemporaryFile(mode='w+b') as tmp_file:
            #    for chunk in cloud_file.iter_content(self.chunk_size):
            #        tmp_file.write(chunk)
            return cloud_file
        raise PermissionDenied()

    @property
    def usable_file(self):
        return self.tmp_file if self.tmp_file else self.file._file

    def load_file_in_tmp(self, delete=True):
        if self.local_available:
            self.tmp_file = self.file.path
        else:
            with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as tmp_file:
                for chunk in self.cloud_file.iter_content(self.chunk_size):
                    tmp_file.write(chunk)
                self.tmp_file = tmp_file

    def remove_file_in_tmp(self):
        os.remove(self.tmp_file.name)

    def http_download(self):
        todl_file = self.cloud_file if self.proxy_cloud_streaming else self.file
        response = FileResponse(todl_file)
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.file_name
        return response


    @property
    def has_reader(self):
        return True if self.reader_path else False
    @property
    def reader(self):
        return import_string(self.reader_path) if self.reader_path else None

    # PROPERTIES
    @property
    def file_url(self): return self.file.url
    @property
    def file_name(self): return self.filename if self.filename else os.path.basename(self.file.name)
    @property
    def valid_file_name(self): return get_valid_filename(self.file.name)
    @property
    def file_extension(self): return os.path.splitext(self.file_name)[-1]
    @property
    def download_url(self): return self.get_url('download', arguments={self.uid_or_pk_arg:self.uid_or_pk})
    @property
    def pdf_url(self): return self.get_url('pdf', arguments={self.uid_or_pk_arg:self.uid_or_pk})
    @property
    def name(self): return self.filename
    @property
    def mime_or_ext(self): return self.filemimetype if self.filemimetype else self.file_extension[1:]
    @property
    def reader_path(self): return self.readers[self.mime_or_ext] if self.mime_or_ext in self.readers else None
            
    # MEMORY FILE
    def InMemoryUploadedFile_filemimetype(self): return self.file._file.content_type
    def InMemoryUploadedFile_size(self): return self.file._file.size
    def InMemoryUploadedFile_charset(self): return self.file._file.charset
    def InMemoryUploadedFile_extracontenttype(self): return self.file._file.content_type_extra
    def InMemoryUploadedFile_filename(self): return os.path.basename(self.file._file.name)

    # SIZE
    def size_long(self, unit=None): return pretty_size_long(self.size, unit) if self.size else None
    def size_short(self, unit=None): return pretty_size_short(self.size, unit) if self.size else None

    # HASHID
    def get_hashid(self): return hashlib.sha1(self.file.read()).hexdigest()
    def set_hashid(self):
        if self.enable_hashid:
            self.hashid = self.get_hashid()

    # THUMBNAIL
    def get_thumbnail(self): return Thumbnail(self.file, self.mime_or_ext)
    def set_thumbnail(self):
        if self.enable_thumbnail:
            self.thumbnail = self.get_thumbnail().base64

    def set_autocomplete(self):
        if self.file._file:
            tmp_file_class = self.file._file.__class__.__name__
            for field in self.auto_complete_fields:
                if hasattr(self, tmp_file_class+"_"+field):
                    setattr(self, field, getattr(self, tmp_file_class+"_"+field)())

    def set_metadata(self):
        if self.has_reader:
            reader = self.reader(file=self.usable_file, filename=self.filename, extension=self.file_extension, reader=True)
            self.metadata = reader.get_meta_data()

    def pre_save_file(self):
        self.set_autocomplete()
        self.set_thumbnail()
        self.set_hashid()
        #self.set_metadata()

    def save(self, *args, **kwargs):
        self.pre_save_file()
        super().save(*args, **kwargs)
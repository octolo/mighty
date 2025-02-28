"""
Model class
Add an image field at the model

[IMAGE_DEFAULT] static image default
(image_url) return the url static/media
(get_mime_type) return the mime type
(image_html) return the html tag <img>
(image_name) return the file name
(valid_image_name) get a valid name for filesystem
(image_extension) return the extension
"""
import base64
import mimetypes
import os

from django.db import models
from django.templatetags.static import static
from django.utils.html import format_html

from mighty.functions import image_directory_path

IMAGE_DEFAULT = 'none.jpg'


class Image(models.Model):
    default_image = 'img/soon.jpg'
    image = models.FileField(upload_to=image_directory_path, blank=True, null=True)
    model_activate_image = True

    class Meta:
        abstract = True

    @property
    def image_url(self): return self.image.url if self.image else static(self.default_image)
    @property
    def get_mime_type(self): return mimetypes.guess_type()[1]
    @property
    def image_html(self): return format_html('<img src="%s" title="%s">' % (self.image.url, str(self)))
    @property
    def image_name(self): return os.path.basename(self.image.name)
    @property
    def valid_image_name(self): return get_valid_filename(self.imagename)
    @property
    def image_extension(self): return os.path.splitext(self.imagename)[1]
    @property
    def imagex16_html(self): return format_html('<img src="%s" title="%s" style="max-height: 16px">' % (self.image_url, str(self)))
    @property
    def image_b64(self): return base64.b64encode(self.image.read()).decode('utf-8')


from django_ckeditor_5.widgets import CKEditor5Widget

class Document(CKEditor5Widget):
    input_type = 'document'

class Classic(CKEditor5Widget):
    input_type = 'classic'

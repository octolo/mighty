from django.db import models
from mighty.applications.grapher.models import Template, Graphic

class Template(Template):
    pass

class Graphic(Graphic):
    templates = models.ManyToManyField(Template)
from django.contrib import admin
from mighty.models.applications.grapher import Template, Graphic
from mighty.applications.grapher.admin import TemplateAdmin, GraphicAdmin

@admin.register(Template)
class TemplateAdmin(TemplateAdmin):
    pass

@admin.register(Graphic)
class GraphicAdmin(GraphicAdmin):
    pass
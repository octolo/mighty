from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.module_loading import import_string

from mighty.views import DetailView
from mighty.views.viewsets import ModelViewSet
from mighty.models.applications.grapher import Graphic
from mighty.applications.grapher import fields

@method_decorator(xframe_options_exempt, name='dispatch')
class GraphicView(DetailView):
    over_no_permission = True
    fields = fields.graphic
    backend = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        backend = import_string(settings.GRAPHER_BACKEND)
        self.backend = backend(self.object)
        context.update({ 'templates': self.object.templates.all() })
        return context

class SvgView(GraphicView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'css': self.backend.css['svg'],
            'html': self.backend.html['svg'],
            'directory': self.backend.directory['svg'],
            'js': self.backend.libraries('svg'),
        })
        return context

class CanvasView(GraphicView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'css': self.backend.css['canvas'],
            'html': self.backend.html['canvas'],
            'directory': self.backend.directory['canvas'],
            'js': self.backend.libraries('canvas'),
        })
        return context

class GraphicViewSet(ModelViewSet):
    model = Graphic
    list_display = ('__str__', 'image_html',)
    fields = fields.graphic
    slug = '<uuid:uid>'
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def __init__(self, model=None):
        super().__init__()
        self.add_view('svg', SvgView, '%s/svg/' % self.slug)
        self.add_view('canvas', CanvasView, '%s/canvas/'% self.slug)
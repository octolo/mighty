from django.urls import path
from mighty import views
from mighty.functions import logger
from copy import deepcopy

view_attr = {
    'add_to_context': {},
    'is_ajax': False,
}

model_attr = (
    'fields',
    'slug',
    'slug_field',
    'slug_url_kwarg',
    'filter_model',
)

class ViewSet(object):
    views = {}
    excluded_views = ()
    add_to_context = {}

    def Vgetattr(self, View, view, attr, default=False):
        if hasattr(self, attr) and getattr(self, attr): default = getattr(self, attr)
        if hasattr(View, "over_%s" % attr) and getattr(View, "over_%s" % attr): default = getattr(View, "over_%s" % attr)
        if hasattr(self, '%s_%s' % (view, attr)) and getattr(self, '%s_%s' % (view, attr)): default = getattr(self, '%s_%s' % (view, attr))
        return default

    def __init__(self):
        self.views = deepcopy(self.views)
        for k in self.excluded_views: del self.views[k]
  
    def add_view(self, name, view, url): 
        self.views[name] = {'view': view, 'url': url}

    def config_view(self, View, view):
        logger("twofactor", "debug", "-- ViewType: %s" % view)
        for attr, default in view_attr.items(): setattr(View, attr, self.Vgetattr(View, view, attr, default))
        if not self.Vgetattr(View, view, 'no_permission', False): View.permission_required = self.Vgetattr(View, view, "permission_required", ())
        return View

    def view(self, view, *args, **kwargs):
        View = type(view, (self.views[view]['view'],), {})
        for k, v in kwargs.items(): setattr(View, k, v)
        return self.config_view(View, view)

    def url(self, view, config): return config['url']
    def url_name(self, view): return '%s-%s' % (str(self.model.__name__.lower()), view)
    @property
    def urls(self):
        logger("mighty", "debug", "- ViewSet: %s" % self.__class__.__name__)
        return [path(self.url(view, config), self.view(view).as_view(), name=self.url_name(view)) for view,config in self.views.items()]

class ModelViewSet(ViewSet):
    model = None
    slug = '<int:id>'
    slug_field = 'id'
    slug_url_kwarg = 'id'
 
    def __init__(self):
        super().__init__()
        self.views = {}
        self.add_view('list', views.ListView, '')
        self.add_view('add', views.AddView, 'add/')
        self.add_view('detail', views.DetailView, '%s/detail/' % self.slug)
        self.add_view('change', views.ChangeView, '%s/change/' % self.slug)
        self.add_view('delete', views.DeleteView, '%s/delete/' % self.slug)
        self.add_view('export', views.ExportView, 'export/')
        #self.add_view('import', views.ImportView, 'import/')
        if hasattr(self.model, 'is_disable'):
            self.add_view('disable', views.DisableView, '%s/disable/' % self.slug)
            self.add_view('enable', views.EnableView, '%s/enable/' % self.slug)
        if hasattr(self.model, 'file'):
            self.add_view('download', views.FileDownloadView, '%s/download/' % self.slug)
            self.add_view('pdf', views.FilePDFView, '%s/pdf/' % self.slug)

    def config_view(self, View, view):
        View = super().config_view(View, view)
        View.model = self.model
        for attr in model_attr: setattr(View, attr, self.Vgetattr(View, view, attr))
        if not self.Vgetattr(View, view, 'no_permission', False): View.permission_required = self.Vgetattr(View, view, "permission_required", (self.model().perm(view),))
        return View

    def url(self, view, config):
        return config['url']

from mighty.views import api as apiviews
from mighty.permissions import HasMightyPermission

class ApiModelViewSet(ModelViewSet):
    permission_classes = [HasMightyPermission]
    lookup_field = 'id'
    queryset = None

    def config_view(self, View, view):
        View = super().config_view(View, view)
        View.permission_classes = self.Vgetattr(View, view, 'permission_classes')
        View.serializer_class = self.Vgetattr(View, view, 'serializer_class', self.model.objects.all())
        View.lookup_field = self.Vgetattr(View, view, 'lookup_field')
        View.queryset = self.queryset
        return View

    def url_name(self, view):
        return 'api-%s-%s' % (str(self.model.__name__.lower()), view)

    def __init__(self):
        super().__init__()
        self.views = {}
        self.add_view('list', apiviews.ListAPIView, '')
        self.add_view('add', apiviews.CreateAPIView, 'add/')
        self.add_view('detail', apiviews.RetrieveAPIView, '%s/detail/' % self.slug)
        self.add_view('change', apiviews.UpdateAPIView, '%s/change/' % self.slug)
        self.add_view('delete', apiviews.DestroyAPIView, '%s/delete/' % self.slug)
        if hasattr(self.model, 'is_disable'):
            self.add_view('disable', apiviews.EnableApiView, '%s/disable/' % self.slug)
            self.add_view('enable', apiviews.DisableApiView, '%s/enable/' % self.slug)
        
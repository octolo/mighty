from django.shortcuts import render
from mighty.functions import url_domain
from mighty.views import DetailView
from mighty.models import Missive

# Create your views here.
class EmailViewer(DetailView):
    model = Missive
    template_name = "messenger/email_viewer.html"
    slug_url_kwarg = "uid"
    slug_field = "uid"

    def get_context_data(self, **kwargs):
        ct = super().get_context_data(**kwargs)
        ct["domain_url"] = url_domain("")
        return ct

    def get_template_names(self):
        obj = self.get_object()
        return obj.template if obj.template else super().get_template_names()
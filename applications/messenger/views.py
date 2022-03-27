from django.shortcuts import render
from mighty.views import DetailView
from mighty.models import Missive

# Create your views here.
class EmailViewer(DetailView):
    model = Missive
    template_name = "messenger/email_viewer.html"
    slug_url_kwarg = "uid"
    slug_field = "uid"

    def get_template_names(self):
        obj = self.get_object()
        return obj.template if obj.template else super().get_template_names()
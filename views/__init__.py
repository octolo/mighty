from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from mighty.views.base import BaseView, ModelView
from mighty.functions import make_searchable

# FormView overrided
class FormView(BaseView, FormView):
    pass

# TemplateView overrided
class TemplateView(BaseView, TemplateView):
    pass

# ListView overrided
class ListView(ModelView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": self.model._meta.verbose_name_plural,})
        return context

# CreateView overrided and rename with an empty object
class AddView(ModelView, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": "%s %s" % (self.model.mighty.perm_title['add'], self.model._meta.verbose_name)})
        return context

    def get_success_url(self):
        return self.object.detail_url

# DetailView overrided
class DetailView(ModelView, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": self.object})
        return context

# ChangeView overrided
class ChangeView(ModelView, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context.update({"title": "%s %s" % (self.model.mighty.perm_title['change'], self.model._meta.verbose_name)})
        return context

    def get_success_url(self):
        return self.object.detail_url

# DeleteView overrided
class DeleteView(ModelView, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": "%s %s" % (self.object.mighty.perm_title['delete'], self.object._meta.verbose_name)})
        return context

    def get_success_url(self):
        return self.object.list_url

# EnableView is like deleteview but set is_disable to false
class EnableView(DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": "%s %s" % (self.model.mighty.perm_title['enable'], context["fake"]._meta.verbose_name)})
        return context

    def get_success_url(self):
        return self.object.detail_url

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.enable()
        return HttpResponseRedirect(success_url)

# EnableView is like deleteview but set is_disable to true
class DisableView(DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": "%s %s" % (self.model.mighty.perm_title['disable'], self.object._meta.verbose_name)})
        return context

    def get_success_url(self):
        return self.object.list_url

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.disable()
        return HttpResponseRedirect(success_url)

# FileDownloadView download file in object model File
class FileDownloadView(BaseView, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        fil = get_object_or_404(self.model, uid=kwargs['uid'])
        return fil.file_url

# FilePDFView open a pdf file in a viewer
class FilePDFView(DetailView):
    pass

# Buffer for ExportView
class Echo:
    def write(self, value): return value

# ExportView download a csv file
class ExportView(ListView):
    def iter_items(self, items, pseudo_buffer):
        writer = csv.writer(pseudo_buffer)
        yield writer.writerow(self.fields)
        for item in items:
            yield writer.writerow(item)

    def render_to_response(self, context, **response_kwargs):
        frmat = self.request.GET.get('format', '')
        if self.filter_model:
            queryset, q = self.filter_model(self.request)
            objects_list = queryset.filter(q).values_list(*self.fields)
        else:
            objects_list = self.model.objects.all().values_list(*self.fields)
        response = StreamingHttpResponse(streaming_content=(self.iter_items(objects_list, Echo())), content_type='text/csv',)
        response['Content-Disposition'] = 'attachment;filename=%s.csv' % get_valid_filename(make_searchable(self.model._meta.verbose_name))
        return response

class HomePageView(TemplateView):
    template_name = 'home.html'

class Widget(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    def get_template_names(self):
        return 'widgets/%s.html' % self.kwargs['widget']
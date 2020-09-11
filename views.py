from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from mighty.models import ConfigClient
from mighty.apps import MightyConfig as conf
from mighty.functions import tpl, tplx
from mighty.functions import make_searchable, setting

import logging
logger = logging.getLogger(__name__)

"""
Standard view without model
app_label + model_name can be faked for supporting reverse_url
[app_label] view application label
[model_name] application model name
[no_permission] if true no permission needed to get the view
[permission_required] list all permissions needed to get the view
[add_to_context] dict to add datas in the context view
"""
class BaseView(PermissionRequiredMixin):
    app_label = None
    model_name = None
    template_name = None
    no_permission = False
    is_ajax = False
    permission_required = ()
    add_to_context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info("view: %s" % self.__class__.__name__, extra={'user': self.request.user})
        context.update({"view": self.__class__.__name__, "perms": self.request.user.get_all_permissions()})
        context.update(self.add_to_context)
        return context

    def get_template_names(self):
        if self.is_ajax: self.template_name = self.template_name or tplx(self.app_label, self.model_name, str(self.__class__.__name__).lower())
        else: self.template_name = self.template_name or tpl(self.app_label, self.model_name, str(self.__class__.__name__).lower())
        logger.debug("template: %s" % self.template_name, extra={'user': self.request.user, 'log_in_db': self.request.user})
        return self.template_name

"""
Standard view without model
app_label + model_name are mandatory
[is_ajax] contains the url if you need to retrieve the data asynchronously
    if is_ajax is configured then ajax templates are also tested
[paginate_by] number of data by page
"""
class ModelView(BaseView):
    is_ajax = False
    paginate_by = conf.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "opts": self.model._meta,
            "fake": self.model(),
        })
        context.update({
            "can_add": self.request.user.has_perm(context["fake"].perm("add")),
            "can_change": self.request.user.has_perm(context["fake"].perm("change")),
            "can_delete": self.request.user.has_perm(context["fake"].perm("delete")),
            "can_export": self.request.user.has_perm(context["fake"].perm("export")),
            "can_import": self.request.user.has_perm(context["fake"].perm("import")),
            "can_disable": self.request.user.has_perm(context["fake"].perm("disable")),
            "can_enable": self.request.user.has_perm(context["fake"].perm("enable")),
        })
        return context

    def get_template_names(self):
        if self.is_ajax:
            self.template_name = self.template_name or tplx(
                self.app_label or str(self.model._meta.app_label).lower(),
                self.model_name or str(self.model.__name__).lower(),
                str(self.__class__.__name__).lower())
        else:
            self.template_name = self.template_name or tpl(
                self.app_label or str(self.model._meta.app_label).lower(),
                self.model_name or str(self.model.__name__).lower(),
                str(self.__class__.__name__).lower())
        logger.info("template: %s" % self.template_name, self.request.user)
        return self.template_name

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
class ViewView(ModelView, DetailView):
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
class FilePDFView(ViewView):
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

class Widget(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    def get_template_names(self):
        return 'widgets/%s.html' % self.kwargs['widget']

if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.generics import DestroyAPIView, RetrieveAPIView
    from rest_framework.response import Response
    from rest_framework import status
    from rest_framework.serializers import ModelSerializer

    # DisableApiView add a view for disable an object (set is_disable to true)
    class DisableApiView(DestroyAPIView):
        def delete(self, request, *args, **kwargs):
            return self.disable(request, *args, **kwargs)

        def disable(self, request, *args, **kwargs):
            instance = self.get_object()
            self.perform_disable(instance)
            return Response(status=status.HTTP_200_OK)

        def perform_disable(self, instance):
            instance.disable()

    # EnableApiView add a view for enable an object (set is_disable to false)
    class EnableApiView(DestroyAPIView):
        def delete(self, request, *args, **kwargs):
            return self.enable(request, *args, **kwargs)

        def enable(self, request, *args, **kwargs):
            instance = self.get_object()
            self.perform_enable(instance)
            return Response(status=status.HTTP_200_OK)

        def perform_enable(self, instance):
            instance.enable()

    class ConfigClientSerializer(ModelSerializer):
        class Meta:
            model = ConfigClient
            fields = ('name', 'config',)

    class ConfigCLientApi(RetrieveAPIView):
        queryset = ConfigClient.objects.all()
        serializer_class = ConfigClientSerializer
        model = ConfigClient
        lookup_field = 'url_name'

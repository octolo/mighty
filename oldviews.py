from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.views import View
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import JsonResponse, HttpResponse, FileResponse, Http404, StreamingHttpResponse
from django.utils.text import get_valid_filename
from django.core.files import File
from django.template.loader import get_template
from django.template import Context, Template
from django.db.models import Q

from mighty import translates as _
from mighty.filters import FiltersManager, Foxid
from mighty.models import ConfigClient, ConfigSimple
from mighty.apps import MightyConfig as conf
from mighty.functions import tpl, tplx
from mighty.functions import make_searchable, setting
from mighty.applications.twofactor.apps import TwofactorConfig
from mighty.applications.nationality.apps import NationalityConfig
from mighty.applications.user import get_form_fields

import pdfkit, os, tempfile, csv, logging

base_config = { 
    'base': {
        'logo': conf.logo,
        'email': TwofactorConfig.method.email,
        'sms': TwofactorConfig.method.sms,
        'basic': TwofactorConfig.method.basic,
        'languages': NationalityConfig.availables,
        'fields': get_form_fields(),
    }}
base_config.update(setting('BASE_CONFIG', {}))
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

class FoxidView(ModelView, BaseView):
    cache_manager = None
    filters = []
    mandatories = ()

    @property
    def check_mandatories(self):
        print(self.request)
        return True

    def foxid(self, queryset):
        if self.check_mandatories:
            return Foxid(queryset, self.request, f=self.manager.flts).ready()
        return PermissionDenied()

    @property
    def manager(self):
        self.cache_manager = self.cache_manager if self.cache_manager else FiltersManager(flts=self.filters, mandatories=self.mandatories)
        return self.cache_manager

    def get_object(self):
        return self.foxid(super().get_queryset()).get(*self.manager.params(self.request))

    def get_queryset(self, queryset=None):
        return self.foxid(super().get_queryset()).filter(*self.manager.params(self.request))

# ListView overrided
class ListView(FoxidView, ListView):
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
class FilePDFView(DetailView):
    pass

# Buffer for ExportView
class StreamingBuffer:
    def write(self, value): return value

# ExportView download a csv file
class ExportView(ListView):
    protect_limit = None

    def iter_items(self, items, pseudo_buffer):
        writer = csv.writer(pseudo_buffer)
        yield writer.writerow(self.fields)
        for item in items:
            yield writer.writerow(item)

    def get_queryset(self, queryset):
        if protect_limit is not None:
            return super().get_queryset(queryset)[0:self.protect_limit]
        return super().get_queryset(queryset)

    def render_to_response(self, context, **response_kwargs):
        frmat = self.request.GET.get('format', '')
        objects_list = self.get_queryset().values_list(*self.fields)
        response = StreamingHttpResponse(streaming_content=(self.iter_items(objects_list, StreamingBuffer())), content_type='text/csv',)
        response['Content-Disposition'] = 'attachment;filename=%s.csv' % get_valid_filename(make_searchable(self.model._meta.verbose_name))
        return response

# Check data side server
class CheckData(TemplateView):
    test_field = None

    def get_data(self):
        return self.request.GET.get('check')

    def get_queryset(self, queryset=None):
        self.model.objects.get(**{self.test_field: self.get_data()})

    def check_data(self):
        try:
            self.get_queryset()
        except self.model.DoesNotExist:        
            return { "message": _.no_errors }
        return { "code": "001", "error": _.error_already_exist }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.check_data(), safe=False, **response_kwargs)


# Return an html widget
class Widget(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    def get_template_names(self):
        return 'widgets/%s.html' % self.kwargs['widget']

# Return the base config of mighty
class Config(TemplateView):
    def get_config(self):
        return base_config

    def get_context_data(self, **kwargs):
        return self.get_config()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

# Return all configs in model ConfigClient
class ConfigListView(ListView):
    model = ConfigClient

    def get_queryset(self):
        return [ConfigClient.objects.filter(is_disable=False), ConfigSimple.objects.filter(is_disable=False)]

    def render_to_response(self, context):
        cfg = base_config
        if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
            from mighty.applications.nationality import conf_prefix_numbering
            cfg.update({"phones": conf_prefix_numbering()})
        for cfgs in context['object_list']:
            cfg.update({cfg.url_name: cfg.config for cfg in cfgs})
        return JsonResponse(cfg)

# Return a named Config
class ConfigDetailView(DetailView):
    model = ConfigClient

    def get_config(self):
        try:
            return ConfigClient.objects.get(url_name=self.kwargs.get('name'))
        except ConfigClient.DoesNotExist:
            return ConfigSimple.objects.get(url_name=self.kwargs.get('name'))

    def get_object(self, queryset=None):
        try:
            return self.get_config()
        except ObjectDoesNotExist:
            raise Http404


    def render_to_response(self, context):
        cfg = self.get_object()
        return JsonResponse({cfg.name: cfg.config})

# Generic response
class GenericSuccess(View):
    def get(self, request):
        return HttpResponse('OK')

import os
class PDFView(DetailView):
    header_html = None
    footer_html = None
    cache_object = None
    in_browser = False
    pdf_name = 'file.pdf'
    options = conf.pdf_options
    header_tpl = conf.pdf_header
    footer_tpl = conf.pdf_footer
    content_html = conf.pdf_content
    tmp_pdf = None

    def get_object(self):
        if not self.cache_object:
            self.cache_object = super().get_object()
        return self.cache_object

    def get_header(self):
        return ""

    def build_header_html(self):
        if not self.header_html:
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as header_html:
                header = self.get_header()
                header_html.write(Template(header).render(self.get_context_data()).encode("utf-8"))
            self.header_html = header_html
        return self.header_html

    def get_footer(self):
        return ""

    def build_footer_html(self):
        if not self.footer_html:
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as footer_html:
                footer = self.get_footer()
                footer_html.write(Template(footer).render(self.get_context_data()).encode("utf-8"))
            self.footer_html = footer_html
        return self.footer_html

    def get_css_print(self):
        return os.path.join(setting('STATIC_ROOT', '/static'), 'css', 'print.css')

    def get_context_data(self, **kwargs):
        return Context({ "obj": self.get_object() })

    def get_options(self):
        self.options.update({
            '--header-html': self.build_header_html().name,
            '--footer-html': self.build_footer_html().name,
        })
        return self.options

    def get_pdf_name(self):
        return self.pdf_name

    def get_tmp_pdf(self, context):
        if not self.tmp_pdf:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                pdfkit.from_string(self.get_template(context), tmp_pdf.name, options=self.get_options())
                self.tmp_pdf = tmp_pdf
        return self.tmp_pdf

    def save_pdf(self, context):
        tmp_pdf = self.get_tmp_pdf(context)

    def get_template(self, context):
        template_name = self.get_template_names()
        template = get_template(template_name)
        return self.content_html % template.render(context)

    def clean_tmp(self):
        if self.header_html and os.path.isfile(self.header_html.name):
            os.remove(self.header_html.name)
        if self.footer_html and os.path.isfile(self.footer_html.name):
            os.remove(self.footer_html.name)
        if self.tmp_pdf and os.path.isfile(self.tmp_pdf.name):
            os.remove(self.tmp_pdf.name)

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('save', False): self.save_pdf(context)
        if self.in_browser:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as tmp_pdf:
                pdf = pdfkit.from_string(self.get_template(context), tmp_pdf.name, options=self.get_options())
                self.clean_tmp()
                return FileResponse(open(tmp_pdf.name, 'rb'), filename=self.get_pdf_name())
        pdf = pdfkit.from_string(self.get_template(context), False, options=self.get_options())
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.get_pdf_name()
        self.clean_tmp()
        return response

if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.decorators import action
    from rest_framework.viewsets import ModelViewSet
    from rest_framework.generics import DestroyAPIView, RetrieveAPIView, ListAPIView
    from rest_framework.response import Response
    from rest_framework import status
    from rest_framework.serializers import ModelSerializer

    # DisableApiView add a view for disable an object (set is_disable to true)
    class DisableApiView(DestroyAPIView):
        def delete(self, request, *args, **kwargs):
            return self.disable(request, *args, **kwargs)

        def disable(self, request, *args, **kwargs):
            instance = self.get_object()
            instance = self.perform_disable(instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        def perform_disable(self, instance):
            instance = instance.disable()
            return instance

    # EnableApiView add a view for enable an object (set is_disable to false)
    class EnableApiView(DestroyAPIView):
        def delete(self, request, *args, **kwargs):
            return self.enable(request, *args, **kwargs)

        def enable(self, request, *args, **kwargs):
            instance = self.get_object()
            instance = self.perform_enable(instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        def perform_enable(self, instance):
            instance = instance.enable()
            return instance

    class CheckData(CheckData, RetrieveAPIView):
        def get(self, request, format=None):
            return Response(self.check_data())

    class ModelViewSet(ModelViewSet):
        cache_manager = None
        filters = []
        user_way = "user"

        # Filter query
        def Q_is_me(self, prefix=""):
            return Q(**{prefix+self.user_way: self.request.user})

        # Queryset
        def get_queryset(self, queryset=None):
            return self.foxid.filter(*self.manager.params(self.request))

        @property
        def foxid(self):
            return Foxid(self.queryset, self.request, f=self.manager.flts).ready()

        @property
        def manager(self):
            if not self.cache_manager:
                self.cache_manager = FiltersManager(flts=self.filters)
            return self.cache_manager

        # Properties
        @property
        def user_groups(self):
            return self.request.user.groups.all()

        @property
        def user_groups_pk(self):
            return [group.pk for group in self.user_groups]

        @property
        def is_staff(self):
            return self.request.user.is_staff

        @property
        def is_superuser(self):
            return self.request.user.is_superuser

        # Actions
        @action(detail=True, methods=['get'])
        def enable(self, request, pk=None):
            instance = self.get_object()
            instance.enable()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        @action(detail=True, methods=['get'])
        def disable(self, request, pk=None):
            instance = self.get_object()
            instance.disable()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

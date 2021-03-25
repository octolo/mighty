from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import JsonResponse, HttpResponse

from mighty import translates as _
from mighty.filters import FiltersManager, Foxid
from mighty.models import ConfigClient
from mighty.apps import MightyConfig as conf
from mighty.functions import tpl, tplx
from mighty.functions import make_searchable, setting
from mighty.applications.twofactor.apps import TwofactorConfig
from mighty.applications.nationality.apps import NationalityConfig
from mighty.applications.user import get_form_fields

base_config = { 
    'base': {
        'logo': conf.logo,
        'email': TwofactorConfig.method.email,
        'sms': TwofactorConfig.method.sms,
        'basic': TwofactorConfig.method.basic,
        'languages': NationalityConfig.availables,
        'fields': get_form_fields()
    }}

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
    cache_manager = None
    filters = []

    def foxid(self, queryset):
        return Foxid(queryset, self.request, f=self.manager.flts).ready()

    @property
    def manager(self):
        self.cache_manager = self.cache_manager if self.cache_manager else FiltersManager(flts=self.filters)
        return self.cache_manager

    def get_queryset(self, queryset=None):
        return self.foxid(super().get_queryset()).filter(*self.manager.params(self.request))

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

# Check data side server
class CheckData(TemplateView):
    test_field = None

    def get_queryset(self, queryset=None):
        self.model.objects.get(**{self.test_field: self.request.GET.get('check')})

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
    queryset = ConfigClient.objects.all()

    def render_to_response(self, context):
        cfg = {cfg.url_name: cfg.config for cfg in context['object_list']}
        cfg.update(base_config)
        return JsonResponse(cfg)

# Return a named ConfigCLient
class ConfigDetailView(DetailView):
    model = ConfigClient

    def get_object(self, queryset=None):
        return ConfigClient.objects.get(url_name=self.kwargs.get('name'))

    def render_to_response(self, context):
        cfg = context['object'].config
        key = self.request.GET.get('key', False)
        return JsonResponse({key: cfg[key]} if key in cfg else cfg)

# Generic response
class GenericSuccess(View):
    def get(self, request):
        return HttpResponse('OK')

from io import BytesIO
from django.core.files import File
from django.template.loader import get_template
from django.template import Context, Template
import pdfkit, os
import tempfile
from django.http import FileResponse
class PDFView(DetailView):
    header_html = None
    footer_html = None
    cache_object = None
    in_browser = False
    pdf_name = 'file.pdf'
    options = {
            'encoding': 'UTF-8',
            'page-size':'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'custom-header' : [
                ('Accept-Encoding', 'gzip')
            ]
        }

    header_footer = doctype = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <script>
    function subst() {
        var vars = {};
        var query_strings_from_url = document.location.search.substring(1).split('&');
        for (var query_string in query_strings_from_url) {
            if (query_strings_from_url.hasOwnProperty(query_string)) {
                var temp_var = query_strings_from_url[query_string].split('=', 2);
                vars[temp_var[0]] = decodeURI(temp_var[1]);
            }
        }
        var css_selector_classes = ['page', 'frompage', 'topage', 'webpage', 'section', 'subsection', 'date', 'isodate', 'time', 'title', 'doctitle', 'sitepage', 'sitepages'];
        for (var css_class in css_selector_classes) {
            if (css_selector_classes.hasOwnProperty(css_class)) {
                var element = document.getElementsByClassName(css_selector_classes[css_class]);
                for (var j = 0; j < element.length; ++j) {
                    element[j].textContent = vars[css_selector_classes[css_class]];
                }
            }
        }
    }
    </script>
  </head>
  <body onload="subst()">%s</body>
</html>"""

    content_html = content = """<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  </head>
  <body>%s</body>
</html>"""

    def get_object(self):
        if not self.cache_object:
            self.cache_object = super().get_object()
        return self.cache_object

    def build_header_html(self):
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as header_html:
            header = self.header_footer % self.get_object().group.build_document_header
            header_html.write(Template(header).render(self.get_context_data()).encode("utf-8"))
        self.header_html = header_html
        return self.header_html

    def build_footer_html(self):
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as footer_html:
            footer = self.header_footer % self.get_object().group.build_document_footer
            footer_html.write(Template(footer).render(self.get_context_data()).encode("utf-8"))
        self.footer_html = footer_html
        return self.footer_html

    def get_css_print(self):
        return os.path.join(settings.STATIC_ROOT, 'css', 'print.css')

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

    def tmp_pdf(self, context):
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            return pdfkit.from_string(self.get_template(context), tmp_pdf.name, options=self.get_options())

    def save_pdf(self, context):
        tmp_pdf = self.tmp_pdf(context)

    def get_template(self, context):
        template_name = self.get_template_names()
        template = get_template(template_name)
        return self.content_html % template.render(context)

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('save', False): self.save_pdf(context)
        if self.in_browser:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                pdf = pdfkit.from_string(self.get_template(context), tmp_pdf.name, options=self.get_options())
                return FileResponse(open(tmp_pdf.name, 'rb'), filename=self.get_pdf_name())
        pdf = pdfkit.from_string(self.get_template(context), False, options=self.get_options())
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.get_pdf_name()
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

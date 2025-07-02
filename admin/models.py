import json
from functools import update_wrapper

from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import (IS_POPUP_VAR, TO_FIELD_VAR,
                                          csrf_protect_m,
                                          get_content_type_for_model)
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import flatten_fieldsets, unquote
from django.contrib.auth import get_permission_codename
from django.core.exceptions import PermissionDenied
from django.db import router, transaction
from django.forms.formsets import all_valid
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django_json_widget.widgets import JSONEditorWidget
from mighty import decorators as decfields
from mighty import fields
from mighty import translates as _m
from mighty.admin.filters import InAlertListFilter, InErrorListFilter
from mighty.fields import JSONField
from mighty.forms import TimelineForm
from mighty.functions import get_form_model, has_model_activate
from mighty.models.source import CHOICES_TYPE


class BaseAdmin(admin.ModelAdmin):
    admin_form_template = None
    disable_selected_confirmation_template = None
    disable_confirmation_template = None
    enable_selected_confirmation_template = None
    enable_confirmation_template = None
    save_on_top = True
    formfield_overrides = {JSONField: {'widget': JSONEditorWidget}}
    access_in_front = False
    queryset = None
    temporary_fields = None
    temporary_fieldsets = None
    temporary_urlname = None
    view_added = None

    def get_form(self, request, obj=None, change=False, **kwargs):
        if kwargs.get('form'):
            return kwargs.get('form')
        return super().get_form(request, obj, change, **kwargs)

    def get_admin_urlname(self, suffix):
        return f'{self.model._meta.app_label}_{self.model._meta.model_name}_{suffix}'

    def is_urlname_temporary(self, request):
        from django.urls import resolve

        url_name = resolve(request.path_info).url_name
        return self.temporary_urlname == url_name

    def temporary_fields_or_fieldsets(self, request, field):
        if (
            field
            and hasattr(self.model, field)
            and self.is_urlname_temporary(request)
        ):
            return getattr(self, getattr(self, field))
        return None

    def _admincustom_view(
        self, request, object_id, extra_context, template, **kwargs
    ):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                f'The field {to_field} cannot be referenced.'
            )

        obj = None
        if object_id:
            obj = self.get_object(request, unquote(object_id), to_field)

        if request.method == 'POST':
            if not self.has_change_permission(request, obj):
                raise PermissionDenied
        elif not self.has_view_or_change_permission(request, obj):
            raise PermissionDenied

        if obj is None and object_id:
            return self._get_obj_does_not_exist_redirect(
                request, self.opts, object_id
            )

        media = self.media
        title = _('View %s')
        context = {
            **self.admin_site.each_context(request),
            'title': kwargs.get('title', title % self.opts.verbose_name),
            'subtitle': str(obj) if obj else None,
            'original': obj,
            'is_popup': IS_POPUP_VAR in request.POST
            or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            'media': media,
            'preserved_filters': self.get_preserved_filters(request),
        }
        if object_id:
            context.update({'object_id': object_id})
        context.update(extra_context or {})
        return self.render_admin_custom(
            request, context, obj=obj, template=template
        )

    def render_admin_custom(self, request, context, template, obj=None):
        context['object_tools_items'] = self.object_tools_items
        app_label = self.opts.app_label
        view_on_site_url = self.get_view_on_site_url(obj)
        context.update({
            'add': False,
            'change': True,
            'custom': True,
            'has_view_permission': self.has_view_permission(request, obj),
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_absolute_url': view_on_site_url is not None,
            'absolute_url': view_on_site_url,
            'opts': self.opts,
            'content_type_id': get_content_type_for_model(self.model).pk,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'to_field_var': TO_FIELD_VAR,
            'is_popup_var': IS_POPUP_VAR,
            'app_label': app_label,
        })
        request.current_app = self.admin_site.name
        return TemplateResponse(request, template, context)

    @csrf_protect_m
    def admincustom_view(
        self, request, object_id=None, extra_context=None, **kwargs
    ):
        self.temporary_urlname = kwargs.get('urlname')
        template = kwargs.pop('template')
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._admincustom_view(
                request, object_id, extra_context, template, **kwargs
            )

    def _adminform_view(
        self,
        request,
        object_id,
        form_url,
        extra_context,
        template=None,
        **kwargs,
    ):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                f'The field {to_field} cannot be referenced.'
            )

        obj = None
        if object_id:
            obj = self.get_object(request, unquote(object_id), to_field)
            if request.method == 'POST':
                if not self.has_change_permission(request, obj):
                    raise PermissionDenied
            elif not self.has_view_or_change_permission(request, obj):
                raise PermissionDenied
        elif request.method == 'POST':
            if not self.has_change_permission(request):
                raise PermissionDenied
        elif not self.has_view_or_change_permission(request):
            raise PermissionDenied

        if obj is None and object_id:
            return self._get_obj_does_not_exist_redirect(
                request, self.opts, object_id
            )

        self.raw_id_fields = kwargs.get('raw_id_fields', self.raw_id_fields)
        fieldsets = kwargs.get('fields', self.get_fieldsets(request, obj))
        ModelForm = self.get_form(
            request,
            obj,
            change=True,
            fields=flatten_fieldsets(fieldsets),
            form=kwargs.get('form'),
        )

        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            formsets, inline_instances = self._create_formsets(
                request,
                form.instance,
                change=True,
            )
            form_validated = form.is_valid()
            if form_validated:
                new_object = self.save_form(request, form, change=True)
            else:
                new_object = form.instance
            if all_valid(formsets) and form_validated:
                if kwargs.get('save_model'):
                    self.save_model(request, new_object, form, True)
                if kwargs.get('save_related'):
                    self.save_related(request, form, formsets, True)
                if kwargs.get('log_msg'):
                    change_message = self.construct_change_message(
                        request, form, formsets, kwargs.get('log_msg')
                    )
                    self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)
            form_validated = False
        else:
            form = ModelForm(instance=obj)
            formsets, inline_instances = self._create_formsets(
                request, obj, change=True
            )

        if not self.has_change_permission(request, obj):
            readonly_fields = flatten_fieldsets(fieldsets)
        else:
            readonly_fields = self.get_readonly_fields(request, obj)
        admin_form = helpers.AdminForm(
            form,
            list(fieldsets),
            # Clear prepopulated fields on a view-only form to avoid a crash.
            self.get_prepopulated_fields(request, obj)
            if self.has_change_permission(request, obj)
            else {},
            readonly_fields,
            model_admin=self,
        )
        media = self.media + admin_form.media

        inline_formsets = self.get_inline_formsets(
            request, formsets, inline_instances, obj
        )
        for inline_formset in inline_formsets:
            media += inline_formset.media

        title = _('View %s')

        context = {
            **self.admin_site.each_context(request),
            'title': kwargs.get('title', title % self.opts.verbose_name),
            'subtitle': str(obj) if obj else None,
            'adminform': admin_form,
            'object_id': object_id,
            'original': obj,
            'is_popup': IS_POPUP_VAR in request.POST
            or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            'media': media,
            'inline_admin_formsets': inline_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'preserved_filters': self.get_preserved_filters(request),
        }

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if (
            request.method == 'POST'
            and not form_validated
            and '_saveasnew' in request.POST
        ):
            context['show_save'] = False
            context['show_save_and_continue'] = False

        context.update(extra_context or {})

        return self.render_admin_form(
            request, context, obj=obj, form_url=form_url, template=template
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_tools_items'] = [
            item for item in self.object_tools_items if item.get('list')
        ]
        return super().changelist_view(request, extra_context=extra_context)

    def changeform_view(
        self, request, object_id=None, form_url='', extra_context=None
    ):
        extra_context = extra_context or {}
        extra_context['object_tools_items'] = [
            item for item in self.object_tools_items if not item.get('list')
        ]
        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def render_admin_form(
        self, request, context, form_url='', obj=None, template=None
    ):
        context['object_tools_items'] = self.object_tools_items
        app_label = self.opts.app_label
        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters(
            {'preserved_filters': preserved_filters, 'opts': self.opts},
            form_url,
        )
        view_on_site_url = self.get_view_on_site_url(obj)
        has_editable_inline_admin_formsets = False
        for inline in context['inline_admin_formsets']:
            if (
                inline.has_add_permission
                or inline.has_change_permission
                or inline.has_delete_permission
            ):
                has_editable_inline_admin_formsets = True
                break
        context.update({
            'add': False,
            'change': True,
            'custom': True,
            'has_view_permission': self.has_view_permission(request, obj),
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_editable_inline_admin_formsets': (
                has_editable_inline_admin_formsets
            ),
            'has_file_field': context['adminform'].form.is_multipart()
            or any(
                admin_formset.formset.is_multipart()
                for admin_formset in context['inline_admin_formsets']
            ),
            'has_absolute_url': view_on_site_url is not None,
            'absolute_url': view_on_site_url,
            'form_url': form_url,
            'opts': self.opts,
            'content_type_id': get_content_type_for_model(self.model).pk,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'to_field_var': TO_FIELD_VAR,
            'is_popup_var': IS_POPUP_VAR,
            'app_label': app_label,
        })
        form_template = template or self.admin_form_template
        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            form_template
            or [
                f'admin/{app_label}/{self.opts.model_name}/change_form.html',
                f'admin/{app_label}/change_form.html',
                'admin/change_form.html',
            ],
            context,
        )

    def get_inlines(self, request, obj):
        return [] if self.is_urlname_temporary(request) else self.inlines

    def get_fields(self, request, obj=None):
        if self.is_urlname_temporary(request):
            return self.temporary_fields or super().get_fields(request, obj)
        return super().get_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if self.is_urlname_temporary(request):
            return self.temporary_fieldsets or super().get_fieldsets(
                request, obj
            )
        return super().get_fieldsets(request, obj)

    @csrf_protect_m
    def adminform_view(
        self, request, object_id=None, form_url='', extra_context=None, **kwargs
    ):
        self.temporary_urlname = kwargs.get('urlname')
        self.temporary_fields = kwargs.get('fields')
        self.temporary_fieldsets = kwargs.get('fieldsets')
        template = kwargs.pop('template')
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._adminform_view(
                request, object_id, form_url, extra_context, template, **kwargs
            )

    def get_queryset(self, request):
        if self.queryset:
            return self.queryset
        return super().get_queryset(request)

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def view_on_site(self, obj):
        return obj.detail_url or False if self.access_in_front else False

    def category_exist(self, category):
        for i in [i for i, x in enumerate(self.fieldsets) if x[0] == category]:
            return i
        return False

    def add_field(self, category, fields):
        if self.fieldsets:
            pos = self.category_exist(category)
            if pos:
                self.fieldsets[pos][1]['fields'] += fields
            else:
                self.fieldsets += (
                    (category, {'classes': ('collapse',), 'fields': fields}),
                )

    def custom_fieldset(self, model, admin_site):
        pass

    def custom_tasklist(self, model, admin_site):
        pass

    def custom_filter(self, model, admin_site):
        pass

    def add_some_fields(self, model, admin_site):
        for field in fields.base:
            if hasattr(model, field):
                self.add_field(_m.informations, (field,))
                self.readonly_fields += (field,)
        for field in fields.source:
            if hasattr(model, field):
                self.add_field(_m.source, (field,))
        for field in fields.keywords:
            if hasattr(model, field):
                self.add_field(_m.informations, (field,))
        for field in fields.immutable:
            if hasattr(model, field):
                self.add_field('immutable', (field,))
        self.custom_fieldset(model, admin_site)
        if hasattr(model, 'task_list'):
            self.add_field('Tasks', ('task_status', 'task_last'))
            self.custom_tasklist(model, admin_site)
        if hasattr(model, 'reporting_list'):
            self.add_field('reporting', decfields.reporting_fields)
        if hasattr(model, 'alerts'):
            self.list_filter += (InAlertListFilter,)
        if hasattr(model, 'errors'):
            self.list_filter += (InErrorListFilter,)
        self.custom_filter(model, admin_site)

    def add_some_readonly_fields(self, model, admin_site):
        if hasattr(model, 'reporting_task_date'):
            self.readonly_fields += ('reporting_task_date',)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.object_tools_items = []
        self.add_some_fields(model, admin_site)
        self.add_some_readonly_fields(model, admin_site)

    def task_view(self, request, object_id, extra_context=None):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        task = request.POST.get('task_list')
        if task:
            obj.start_task(task)
            messages.success(request, f'Task start: {task}')
        else:
            messages.warning(request, 'No task start')
        return redirect(obj.admin_change_url)

    def reporting_view(self, request, object_id, extra_context=None):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        response = obj.reporting_execute(request)
        if response:
            return response
        messages.warning(request, 'No reporting to do')
        return redirect(obj.admin_change_url)

    def has_enable_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('enable', opts)
        return request.user.has_perm(f'{opts.app_label}.{codename}')

    def has_disable_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('disable', opts)
        return request.user.has_perm(f'{opts.app_label}.{codename}')

    def disable_model(self, request, obj):
        """Given a model instance disable it from the database."""
        obj.disable()

    @transaction.atomic
    def disable_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        for o in queryset:
            o.disable()

    def log_enablion(self, request, object, object_repr):
        """
        Log that an object will be deleted. Note that this method must be
        called before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import DELETION, LogEntry

        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=object_repr,
            action_flag=DELETION,
        )

    def enable_model(self, request, obj):
        """Given a model instance enable it from the database."""
        obj.enable()

    @transaction.atomic
    def enable_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        for o in queryset:
            o.enable()

    def get_queryset_by_contenttype(self, model, request):
        qs = model._default_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_object_by_contenttype(
        self, request, contenttype_id, object_id, from_field=None
    ):
        from django.contrib.contenttypes.models import ContentType
        from django.core.exceptions import ValidationError

        model = ContentType.objects.get(id=contenttype_id).model_class()
        queryset = self.get_queryset_by_contenttype(model, request)
        field = (
            model._meta.pk
            if from_field is None
            else model._meta.get_field(from_field)
        )
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

    def wrap(self, view, object_tools=None):
        if object_tools:
            self.object_tools_items.append(object_tools)

        def wrapper(*args, **kwargs):
            return self.admin_site.admin_view(view)(*args, **kwargs)

        wrapper.model_admin = self
        return update_wrapper(wrapper, view)

    ##########################
    # timeline Admin
    ##########################
    def timeline_view(
        self, request, contenttype_id, object_id, extra_context=None
    ):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object_by_contenttype(
            request, contenttype_id, unquote(object_id), to_field
        )
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'fake': obj.timeline_model(),
            'timeline': obj.timeline_model.objects.filter(object_id=obj),
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        return TemplateResponse(request, 'admin/timeline_list.html', context)

    def timeline_addfield_view(
        self, request, contenttype_id, object_id, fieldname, extra_context=None
    ):
        info = self.model._meta.app_label, self.model._meta.model_name
        form_conf = {
            'form_class': TimelineForm,
            'form_fields': ['date_begin', 'date_end'],
        }
        form = get_form_model(self.model.timeline_model, **form_conf)
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object_by_contenttype(
            request, contenttype_id, unquote(object_id), to_field
        )
        if request.POST:
            form = form(obj, fieldname, request.user, request.POST)
            if form.is_valid():
                return redirect(
                    'admin:{}_{}_timeline'.format(*info),
                    object_id=object_id,
                    contenttype_id=contenttype_id,
                )
        else:
            form = form(obj, fieldname, request.user)
        context = {
            **self.admin_site.each_context(request),
            'form': form,
            'fieldname': fieldname,
            'object_name': str(opts.verbose_name),
            'object': obj,
            'fake': obj.timeline_model(),
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        return TemplateResponse(
            request, 'admin/timeline_addfield.html', context
        )

    ##########################
    # Source Admin
    ##########################
    def source_view(
        self, request, contenttype_id, object_id, extra_context=None
    ):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object_by_contenttype(
            request, contenttype_id, unquote(object_id), to_field
        )
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'fake': obj.timeline_model(),
            'histories': obj.timeline_model.objects.filter(model_id=object_id),
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        return TemplateResponse(request, 'admin/timeline_list.html', context)

    def source_choice_view(
        self, request, contenttype_id, object_id, fieldname, extra_context=None
    ):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object_by_contenttype(
            request, contenttype_id, unquote(object_id), to_field
        )
        context = {
            **self.admin_site.each_context(request),
            'choices': CHOICES_TYPE,
            'fieldname': fieldname,
            'object_name': str(opts.verbose_name),
            'object': obj,
            'fake': obj.source_model(),
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        return TemplateResponse(request, 'admin/source_choice.html', context)

    def source_addfield_view(
        self,
        request,
        contenttype_id,
        object_id,
        fieldname,
        sourcetype,
        extra_context=None,
    ):
        info = self.model._meta.app_label, self.model._meta.model_name
        form_conf = {
            'form_class': TimelineForm,
            'form_fields': ['date_begin', 'date_end'],
        }
        form = get_form_model(self.model.timeline_model, **form_conf)
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object_by_contenttype(
            request, contenttype_id, unquote(object_id), to_field
        )
        if request.POST:
            form = form(obj, fieldname, request.user, request.POST)
            if form.is_valid():
                return redirect(
                    'admin:{}_{}_timeline'.format(*info), object_id=object_id
                )
        else:
            form = form(obj, fieldname, request.user)
        context = {
            **self.admin_site.each_context(request),
            'sourcetype': sourcetype,
            'form': form,
            'fieldname': fieldname,
            'object_name': str(opts.verbose_name),
            'object': obj,
            'fake': obj.source_model(),
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        return TemplateResponse(request, 'admin/source_addfield.html', context)

    def filemetadata_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        obj.load_file_in_tmp(delete=False)
        obj.set_metadata()
        obj.save()
        obj.remove_file_in_tmp()
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/file_metadata.html', context)

    def variables_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        obj.eve_create_template_variable()
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(
            request, 'admin/template_variable.html', context
        )

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path(
                '<path:object_id>/disable/',
                self.wrap(self.disable_view),
                name='{}_{}_disable'.format(*info),
            ),
            path(
                '<path:object_id>/enable/',
                self.wrap(self.enable_view),
                name='{}_{}_enable'.format(*info),
            ),
            path(
                '<path:object_id>/cachefield/',
                self.wrap(self.cachefield_view),
                name='{}_{}_cache_field'.format(*info),
            ),
            path(
                '<path:object_id>/logsfield/',
                self.wrap(self.logsfield_view),
                name='{}_{}_logs_field'.format(*info),
            ),
            path(
                '<path:object_id>/task/',
                self.wrap(self.task_view),
                name='{}_{}_task'.format(*info),
            ),
            path(
                '<path:object_id>/reporting/',
                self.wrap(self.reporting_view),
                name='{}_{}_reporting'.format(*info),
            ),
        ]

        if (
            hasattr(self.model, 'has_eve_variable_template')
            and self.model.has_eve_variable_template
        ):
            my_urls.append(
                path(
                    '<path:object_id>/variables/',
                    self.wrap(self.variables_view),
                    name='{}_{}_variables'.format(*info),
                )
            )

        if (
            hasattr(self.model, 'enable_model_change_log')
            and self.model.enable_model_change_log
        ):
            my_urls.append(
                path(
                    '<path:object_id>/modelchangelog/',
                    self.wrap(self.modelchangelog_view),
                    name='{}_{}_modelchangelog'.format(*info),
                )
            )

        if has_model_activate(self.model, 'file'):
            my_urls.append(
                path(
                    '<path:object_id>/filemetadata/',
                    self.wrap(self.filemetadata_view),
                    name='{}_{}_filemetadata'.format(*info),
                )
            )

        if hasattr(self.model, 'timeline_model'):
            my_urls += [
                path(
                    'ct-<int:contenttype_id>/<path:object_id>/timeline/',
                    self.wrap(self.timeline_view),
                    name='{}_{}_timeline'.format(*info),
                ),
                path(
                    'ct-<int:contenttype_id>/<path:object_id>/timeline/<str:fieldname>/',
                    self.wrap(self.timeline_addfield_view),
                    name='{}_{}_timeline_addfield'.format(*info),
                ),
            ]
        if hasattr(self.model, 'source_model'):
            my_urls += [
                path(
                    'ct-<int:contenttype_id>/<path:object_id>/source/',
                    self.wrap(self.source_view),
                    name='{}_{}_source'.format(*info),
                ),
                path(
                    'ct-<int:contenttype_id>/<path:object_id>/source/<str:fieldname>/',
                    self.wrap(self.source_choice_view),
                    name='{}_{}_source_choice'.format(*info),
                ),
                path(
                    'ct-<int:contenttype_id>/<path:object_id>/source/<str:fieldname>/<str:sourcetype>/',
                    self.wrap(self.source_addfield_view),
                    name='{}_{}_source_addfield'.format(*info),
                ),
            ]
        return my_urls + urls

    def cachefield_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/cache_field.html', context)

    def logsfield_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media,
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/logs_field.html', context)

    def modelchangelog_view(self, request, object_id, extra_context=None):
        from django.core.paginator import Paginator
        from mighty.models import ModelChangeLog

        opts = self.model._meta
        fake = ModelChangeLog()
        optslog = fake._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        obj = self.get_object(request, unquote(object_id), to_field)
        paginator = Paginator(obj.model_change_logs, 25)
        page = request.GET.get('page', 1)
        context = {
            **self.admin_site.each_context(request),
            'object_name': str(opts.verbose_name),
            'object': obj,
            'logs': paginator.get_page(page),
            'opts': opts,
            'optslog': optslog,
            'app_label': opts.app_label,
            'media': self.media,
            'fake': fake,
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/change_logs.html', context)

    @csrf_protect_m
    def disable_view(self, request, object_id, extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._disable_view(request, object_id, extra_context)

    def _disable_view(self, request, object_id, extra_context):
        """The 'disable' admin view for this model."""
        opts = self.model._meta
        app_label = opts.app_label

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                f'The field {to_field} cannot be referenced.'
            )

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_disable_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            return self._get_obj_does_not_exist_redirect(
                request, opts, object_id
            )

        # Populate disabled_objects, a data structure of all related objects that
        # will also be disabled.
        disabled_objects, model_count, perms_needed, protected = (
            self.get_deleted_objects([obj], request)
        )

        if (
            request.POST and not protected
        ):  # The user has confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = str(obj)
            attr = str(to_field) if to_field else opts.pk.attname
            obj_id = obj.serializable_value(attr)
            self.log_deletion(request, obj, obj_display)
            self.disable_model(request, obj)

            return self.response_disable(request, obj_display, obj_id)

        object_name = str(opts.verbose_name)
        title = (
            _m.can % {'name': object_name}
            if perms_needed or protected
            else _m.are_you_sure
        )

        context = {
            **self.admin_site.each_context(request),
            'title': title,
            'object_name': object_name,
            'object': obj,
            'disabled_objects': disabled_objects,
            'model_count': dict(model_count).items(),
            'perms_lacking': perms_needed,
            'protected': protected,
            'opts': opts,
            'app_label': app_label,
            'preserved_filters': self.get_preserved_filters(request),
            'is_popup': IS_POPUP_VAR in request.POST
            or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            **(extra_context or {}),
        }
        return self.render_disable_form(request, context)

    def response_disable(self, request, obj_display, obj_id):
        """Determine the HttpResponse for the disable_view stage."""
        opts = self.model._meta

        if IS_POPUP_VAR in request.POST:
            popup_response_data = json.dumps({
                'action': 'disable',
                'value': str(obj_id),
            })
            return TemplateResponse(
                request,
                self.popup_response_template
                or [
                    f'admin/{opts.app_label}/{opts.model_name}/popup_response.html',
                    f'admin/{opts.app_label}/popup_response.html',
                    'admin/popup_response.html',
                ],
                {
                    'popup_response_data': popup_response_data,
                },
            )

        self.message_user(
            request,
            _m.disable_ok % {'name': opts.verbose_name, 'obj': obj_display},
            messages.SUCCESS,
        )
        if self.has_change_permission(request, None):
            post_url = reverse(
                f'admin:{opts.app_label}_{opts.model_name}_changelist',
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts}, post_url
            )
        else:
            post_url = reverse('admin:index', current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def render_disable_form(self, request, context):
        opts = self.model._meta
        app_label = opts.app_label
        request.current_app = self.admin_site.name
        context.update(
            to_field_var=TO_FIELD_VAR,
            is_popup_var=IS_POPUP_VAR,
            media=self.media,
        )
        return TemplateResponse(
            request,
            self.disable_confirmation_template
            or [
                f'admin/{app_label}/{opts.model_name}/disable_confirmation.html',
                f'admin/{app_label}/disable_confirmation.html',
                'admin/disable_confirmation.html',
            ],
            context,
        )

    @csrf_protect_m
    def enable_view(self, request, object_id, extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._enable_view(request, object_id, extra_context)

    def _enable_view(self, request, object_id, extra_context):
        """The 'enable' admin view for this model."""
        opts = self.model._meta
        app_label = opts.app_label

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                f'The field {to_field} cannot be referenced.'
            )

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_enable_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            return self._get_obj_does_not_exist_redirect(
                request, opts, object_id
            )

        # Populate enabled_objects, a data structure of all related objects that
        # will also be enabled.
        enabled_objects, model_count, perms_needed, protected = (
            self.get_deleted_objects([obj], request)
        )

        if (
            request.POST and not protected
        ):  # The user has confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = str(obj)
            attr = str(to_field) if to_field else opts.pk.attname
            obj_id = obj.serializable_value(attr)
            self.log_deletion(request, obj, obj_display)
            self.enable_model(request, obj)

            return self.response_enable(request, obj_display, obj_id)

        object_name = str(opts.verbose_name)
        title = (
            _m.cannot_enable % {'name': object_name}
            if perms_needed or protected
            else _m.are_you_sure
        )

        context = {
            **self.admin_site.each_context(request),
            'title': title,
            'object_name': object_name,
            'object': obj,
            'enabled_objects': enabled_objects,
            'model_count': dict(model_count).items(),
            'perms_lacking': perms_needed,
            'protected': protected,
            'opts': opts,
            'app_label': app_label,
            'preserved_filters': self.get_preserved_filters(request),
            'is_popup': IS_POPUP_VAR in request.POST
            or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            **(extra_context or {}),
        }
        return self.render_enable_form(request, context)

    def response_enable(self, request, obj_display, obj_id):
        """Determine the HttpResponse for the enable_view stage."""
        opts = self.model._meta

        if IS_POPUP_VAR in request.POST:
            popup_response_data = json.dumps({
                'action': 'enable',
                'value': str(obj_id),
            })
            return TemplateResponse(
                request,
                self.popup_response_template
                or [
                    f'admin/{opts.app_label}/{opts.model_name}/popup_response.html',
                    f'admin/{opts.app_label}/popup_response.html',
                    'admin/popup_response.html',
                ],
                {
                    'popup_response_data': popup_response_data,
                },
            )

        self.message_user(
            request,
            _m.enable_ok % {'name': opts.verbose_name, 'obj': obj_display},
            messages.SUCCESS,
        )
        if self.has_change_permission(request, None):
            post_url = reverse(
                f'admin:{opts.app_label}_{opts.model_name}_changelist',
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts}, post_url
            )
        else:
            post_url = reverse('admin:index', current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def render_enable_form(self, request, context):
        opts = self.model._meta
        app_label = opts.app_label
        request.current_app = self.admin_site.name
        context.update(
            to_field_var=TO_FIELD_VAR,
            is_popup_var=IS_POPUP_VAR,
            media=self.media,
        )
        return TemplateResponse(
            request,
            self.enable_confirmation_template
            or [
                f'admin/{app_label}/{opts.model_name}/enable_confirmation.html',
                f'admin/{app_label}/enable_confirmation.html',
                'admin/enable_confirmation.html',
            ],
            context,
        )

from django.contrib import admin, messages
from django.db import router, transaction
from django.contrib.auth import get_permission_codename
from django.contrib.admin.options import csrf_protect_m, IS_POPUP_VAR, TO_FIELD_VAR, get_content_type_for_model
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import get_deleted_objects, unquote
from django.template.response import TemplateResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django_json_widget.widgets import JSONEditorWidget

from mighty import fields
from mighty.fields import JSONField
from mighty import translates as _
from mighty.admin.actions import disable_selected, enable_selected
from mighty.admin.filters import InAlertListFilter, InErrorListFilter

from functools import update_wrapper

class BaseAdmin(admin.ModelAdmin):
    disable_selected_confirmation_template = None
    disable_confirmation_template = None
    enable_selected_confirmation_template = None
    enable_confirmation_template = None
    save_on_top = True
    formfield_overrides = {JSONField: {'widget': JSONEditorWidget},}

    def view_on_site(self, obj):
        return obj.detail_url

    def category_exist(self, category):
        for i in [i for i,x in enumerate(self.fieldsets) if x[0] == category]:
            return i
        return False

    def add_field(self, category, fields):
        if self.fieldsets:
            pos = self.category_exist(category)
            if pos: self.fieldsets[pos][1]['fields'] += fields
            else: self.fieldsets += ((category, {'classes': ('collapse',), 'fields': fields},),)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        for field in fields.image:
            if hasattr(model, field):
                self.add_field(_.more, (field,))
        for field in fields.base:
            if hasattr(model, field):
                self.add_field(_.informations, (field,))
                self.readonly_fields += (field,)
        for field in fields.source:
            if hasattr(model, field):
                self.add_field(_.source, (field,))
        for field in fields.keywords:
            if hasattr(model, field):
                self.add_field(_.more, (field,))
        if hasattr(model, 'alerts'): self.list_filter += (InAlertListFilter,)
        if hasattr(model, 'errors'): self.list_filter += (InErrorListFilter,)

    def save_model(self, request, obj, form, change):
        if not change or not obj.create_by:
            if hasattr(obj, 'update_by'): obj.create_by = getattr(request.user, 'logname', 'username')
        if hasattr(obj, 'update_by'): obj.update_by = getattr(request.user, 'logname', 'username')
        super().save_model(request, obj, form, change)

    def has_enable_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('enable', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_disable_permission(self, request, obj=None):
        opts = self.opts
        codename = get_permission_codename('disable', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def disable_model(self, request, obj):
        """
        Given a model instance disable it from the database.
        """
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
        from django.contrib.admin.models import LogEntry, DELETION
        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=object_repr,
            action_flag=DELETION,
        )

    def enable_model(self, request, obj):
        """
        Given a model instance enable it from the database.
        """
        obj.enable()

    @transaction.atomic
    def enable_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        for o in queryset:
            o.enable()

    def log_enablion(self, request, object, object_repr):
        """
        Log that an object will be deleted. Note that this method must be
        called before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, DELETION
        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=object_repr,
            action_flag=DELETION,
        )

    def logs_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        context = {
            **self.admin_site.each_context(request),
            #'title': object_name,
            'object_name': str(opts.verbose_name),
            'object': self.get_object(request, unquote(object_id), to_field),
            'opts': opts,
            'app_label': opts.app_label,
            'media': self.media
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, 'admin/logs.html', context)

    def wrap(self, view):
        def wrapper(*args, **kwargs):
            return self.admin_site.admin_view(view)(*args, **kwargs)
        wrapper.model_admin = self
        return update_wrapper(wrapper, view)

    def get_urls(self):
        from django.urls import path
        urls = super(BaseAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        my_urls = [
            path('<path:object_id>/disable/', self.wrap(self.disable_view), name='%s_%s_disable' % info),
            path('<path:object_id>/enable/', self.wrap(self.enable_view), name='%s_%s_enable' % info),
        ]
        return my_urls + urls

    @csrf_protect_m
    def disable_view(self, request, object_id, extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._disable_view(request, object_id, extra_context)

    def _disable_view(self, request, object_id, extra_context):
        "The 'disable' admin view for this model."
        opts = self.model._meta
        app_label = opts.app_label

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_disable_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        # Populate disabled_objects, a data structure of all related objects that
        # will also be disabled.
        disabled_objects, model_count, perms_needed, protected = self.get_deleted_objects([obj], request)

        if request.POST and not protected:  # The user has confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = str(obj)
            attr = str(to_field) if to_field else opts.pk.attname
            obj_id = obj.serializable_value(attr)
            self.log_deletion(request, obj, obj_display)
            self.disable_model(request, obj)

            return self.response_disable(request, obj_display, obj_id)

        object_name = str(opts.verbose_name)
        title = _.can % {"name": object_name} if perms_needed or protected else _.are_you_sure

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
            'is_popup': IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            **(extra_context or {}),
        }
        return self.render_disable_form(request, context)

    def response_disable(self, request, obj_display, obj_id):
        """
        Determine the HttpResponse for the disable_view stage.
        """
        opts = self.model._meta

        if IS_POPUP_VAR in request.POST:
            popup_response_data = json.dumps({
                'action': 'disable',
                'value': str(obj_id),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                'popup_response_data': popup_response_data,
            })

        self.message_user( request, _.disable_ok % { 'name': opts.verbose_name, 'obj': obj_display, }, messages.SUCCESS)
        if self.has_change_permission(request, None):
            post_url = reverse(
                'admin:%s_%s_changelist' % (opts.app_label, opts.model_name),
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
        context.update( to_field_var=TO_FIELD_VAR, is_popup_var=IS_POPUP_VAR, media=self.media,)
        return TemplateResponse(request,
            self.disable_confirmation_template or [
                "admin/%s/%s/disable_confirmation.html"% (app_label, opts.model_name),
                "admin/%s/disable_confirmation.html" % app_label ,
                "admin/disable_confirmation.html",], context,)

    @csrf_protect_m
    def enable_view(self, request, object_id, extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._enable_view(request, object_id, extra_context)

    def _enable_view(self, request, object_id, extra_context):
        "The 'enable' admin view for this model."
        opts = self.model._meta
        app_label = opts.app_label

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_enable_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        # Populate enabled_objects, a data structure of all related objects that
        # will also be enabled.
        enabled_objects, model_count, perms_needed, protected = self.get_deleted_objects([obj], request)

        if request.POST and not protected:  # The user has confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = str(obj)
            attr = str(to_field) if to_field else opts.pk.attname
            obj_id = obj.serializable_value(attr)
            self.log_deletion(request, obj, obj_display)
            self.enable_model(request, obj)

            return self.response_enable(request, obj_display, obj_id)

        object_name = str(opts.verbose_name)
        title = _.cannot_enable % {"name": object_name} if perms_needed or protected else _.are_you_sure

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
            'is_popup': IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            **(extra_context or {}),
        }
        return self.render_enable_form(request, context)

    def response_enable(self, request, obj_display, obj_id):
        """
        Determine the HttpResponse for the enable_view stage.
        """
        opts = self.model._meta

        if IS_POPUP_VAR in request.POST:
            popup_response_data = json.dumps({
                'action': 'enable',
                'value': str(obj_id),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                'popup_response_data': popup_response_data,
            })

        self.message_user(request, _.enable_ok % {'name': opts.verbose_name,'obj': obj_display,}, messages.SUCCESS, )
        if self.has_change_permission(request, None):
            post_url = reverse(
                'admin:%s_%s_changelist' % (opts.app_label, opts.model_name),
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
        context.update( to_field_var=TO_FIELD_VAR, is_popup_var=IS_POPUP_VAR, media=self.media, )
        return TemplateResponse(request,
            self.enable_confirmation_template or [
                "admin/%s/%s/enable_confirmation.html" % (app_label, opts.model_name),
                "admin/%s/enable_confirmation.html" % app_label,
                "admin/enable_confirmation.html",], context,)
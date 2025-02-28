from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse

from mighty import translates as _


def disable_selected(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    disableable_objects, model_count, perms_needed, protected = modeladmin.get_deleted_objects(queryset, request)
    if request.POST.get('post') and not protected:
        if perms_needed:
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                obj_display = str(obj)
                modeladmin.log_enablion(request, obj, obj_display)
            modeladmin.disable_queryset(request, queryset)
            modeladmin.message_user(request, _.disable_succes % {
                'count': n, 'items': model_ngettext(modeladmin.opts, n)
            }, messages.SUCCESS)
        return None
    objects_name = model_ngettext(queryset)
    title = _.can_not_disable % {'name': objects_name} if perms_needed or protected else _.are_you_sure
    context = {
        **modeladmin.admin_site.each_context(request),
        'title': title,
        'objects_name': str(objects_name),
        'disableable_objects': [disableable_objects],
        'model_count': dict(model_count).items(),
        'queryset': queryset,
        'perms_lacking': perms_needed,
        'protected': protected,
        'opts': opts,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'media': modeladmin.media,
    }
    request.current_app = modeladmin.admin_site.name
    return TemplateResponse(request, modeladmin.disable_selected_confirmation_template or [
        'admin/%s/%s/disable_selected_confirmation.html' % (app_label, opts.model_name),
        'admin/%s/disable_selected_confirmation.html' % app_label,
        'admin/disable_selected_confirmation.html'], context)


disable_selected.allowed_permissions = ('change',)
disable_selected.short_description = _.disable_selected


def enable_selected(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    enableable_objects, model_count, perms_needed, protected = modeladmin.get_deleted_objects(queryset, request)
    if request.POST.get('post') and not protected:
        if perms_needed:
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                obj_display = str(obj)
                modeladmin.log_enablion(request, obj, obj_display)
            modeladmin.enable_queryset(request, queryset)
            modeladmin.message_user(request, _.enable_success % {
                'count': n, 'items': model_ngettext(modeladmin.opts, n)
            }, messages.SUCCESS)
        return None
    objects_name = model_ngettext(queryset)
    title = _.can_not_enable % {'name': objects_name} if perms_needed or protected else _.are_you_sure
    context = {
        **modeladmin.admin_site.each_context(request),
        'title': title,
        'objects_name': str(objects_name),
        'enableable_objects': [enableable_objects],
        'model_count': dict(model_count).items(),
        'queryset': queryset,
        'perms_lacking': perms_needed,
        'protected': protected,
        'opts': opts,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'media': modeladmin.media,
    }
    request.current_app = modeladmin.admin_site.name
    return TemplateResponse(request, modeladmin.enable_selected_confirmation_template or [
        'admin/%s/%s/enable_selected_confirmation.html' % (app_label, opts.model_name),
        'admin/%s/enable_selected_confirmation.html' % app_label,
        'admin/enable_selected_confirmation.html'], context)


enable_selected.allowed_permissions = ('change',)
enable_selected.short_description = _.enable_selected

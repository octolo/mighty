from django.db import router
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from django.utils.text import capfirst


def get_disabled_objects(objs, request, admin_site):
    try:
        obj = objs[0]
    except IndexError:
        return [], {}, set(), []
    else:
        using = router.db_for_write(obj._meta.model)
    collector = NestedObjects(using=using)
    collector.collect(objs)
    perms_needed = set()

    def format_callback(obj):
        model = obj.__class__
        has_admin = model in admin_site._registry
        opts = obj._meta
        no_edit_link = f'{capfirst(opts.verbose_name)}: {obj}'
        if has_admin:
            if not admin_site._registry[model].has_delete_permission(request, obj):
                perms_needed.add(opts.verbose_name)
            try:
                admin_url = reverse(f'{admin_site.name}:{opts.app_label}_{opts.model_name}_disable', None, (quote(obj.pk),))
            except NoReverseMatch:
                return no_edit_link
            return format_html('{}: <a href="{}">{}</a>', capfirst(opts.verbose_name), admin_url, obj)
        return no_edit_link
    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}
    return to_delete, model_count, perms_needed, protected


def get_enabled_objects(objs, request, admin_site):
    try:
        obj = objs[0]
    except IndexError:
        return [], {}, set(), []
    else:
        using = router.db_for_write(obj._meta.model)
    collector = NestedObjects(using=using)
    collector.collect(objs)
    perms_needed = set()

    def format_callback(obj):
        model = obj.__class__
        has_admin = model in admin_site._registry
        opts = obj._meta
        no_edit_link = f'{capfirst(opts.verbose_name)}: {obj}'
        if has_admin:
            if not admin_site._registry[model].has_delete_permission(request, obj):
                perms_needed.add(opts.verbose_name)
            try:
                admin_url = reverse(f'{admin_site.name}:{opts.app_label}_{opts.model_name}_enable', None, (quote(obj.pk),))
            except NoReverseMatch:
                return no_edit_link
            return format_html('{}: <a href="{}">{}</a>', capfirst(opts.verbose_name), admin_url, obj)
        return no_edit_link
    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}
    return to_delete, model_count, perms_needed, protected

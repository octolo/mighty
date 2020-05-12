from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import Group

from mighty.admin.site import AdminSite

#mysite = AdminSite()
#admin.site = mysite
#admin.sites.site = mysite

if 'mighty.applications.user' in settings.INSTALLED_APPS:
    from mighty.admin.applications import user

if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
    from mighty.admin.applications import twofactor

if 'mighty.applications.nationality' in settings.INSTALLED_APPS:
    from mighty.admin.applications import nationality

if 'mighty.applications.grapher' in settings.INSTALLED_APPS:
    from mighty.admin.applications import grapher

#from django.apps import apps
#apps.get_model('auth.Group')._meta.app_label = 'mighty'
#apps.get_model('auth.Group')._meta.db_table = 'mighty_group'
#apps.get_model('auth.Permission')._meta.app_label = 'mighty'
#apps.get_model('auth.Permission')._meta.db_table = 'mighty_permission'

#def render_change_form(self, request, context, *args, **kwargs):
#    if hasattr(kwargs['obj'], 'company'):
#        replace_args = {"company": kwargs['obj'].company}
#        if kwargs['obj'].sql_date_start is not None:
#            replace_args["sql_date_start__lte"] = kwargs['obj'].sql_date_start
#        context['adminform'].form.fields['replace'].queryset = context['adminform'].form.fields['replace'].queryset.filter(**replace_args)
#        resolution_args = {"assembly__company": kwargs['obj'].company}
#        context['adminform'].form.fields['resolution'].queryset = context['adminform'].form.fields['resolution'].queryset.filter(**resolution_args)
#        ag_leave_args = {"company": kwargs['obj'].company}
#        if kwargs['obj'].resolution is not None:
#            ag_leave_args["date_assembly__gt"] = kwargs['obj'].resolution.assembly.date_assembly
#        context['adminform'].form.fields['ag_leave'].queryset = context['adminform'].form.fields['ag_leave'].queryset.filter(**ag_leave_args)
#    else:
#        context['adminform'].form.fields['replace'].queryset = context['adminform'].form.fields['resolution'].queryset.none()
#        context['adminform'].form.fields['resolution'].queryset = context['adminform'].form.fields['resolution'].queryset.none()
#        context['adminform'].form.fields['ag_leave'].queryset = context['adminform'].form.fields['ag_leave'].queryset.none()
#    return super(MandateAdmin, self).render_change_form(request, context, *args, **kwargs)

#def get_form(self, request, obj=None, **kwargs):
#    request._obj_ = obj
#    return super(MandateAdmin, self).get_form(request, obj, **kwargs)

#def __init__(self, model, admin_site):
#    super().__init__(model, admin_site)

#def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
#    field = super(MandateAGDataAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#    if db_field.name == 'assembly':
#        if request._obj_:
#            args = {"company": request._obj_.company}
#            if request._obj_.resolution is not None:
#                args["date_assembly__gte"] = request._obj_.resolution.assembly.date_assembly
#            field.queryset = field.queryset.filter(**args)
#        else: field.queryset = field.queryset.none()
#    if db_field.name == 'renewal':
#        if request._obj_:
#            args = {"assembly__company": request._obj_.company}
#            if request._obj_.resolution is not None:
#                args["assembly__date_assembly__gte"] = request._obj_.resolution.assembly.date_assembly
#            field.queryset = field.queryset.filter(**args)
#        else: field.queryset = field.queryset.none()
#    if db_field.name == 'revocation':
#        if request._obj_:
#            args = {"assembly__company": request._obj_.company}
#            if request._obj_.resolution is not None:
#                args["assembly__date_assembly__gte"] = request._obj_.resolution.assembly.date_assembly
#            field.queryset = field.queryset.filter(**args)
#        else: field.queryset = field.queryset.none()
#    return field

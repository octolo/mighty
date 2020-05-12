from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from mighty.apps import MightyConfig as conf
from mighty.functions import tpl, tplx, logger

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
        logger("mighty", "info", "view: %s" % self.__class__.__name__, self.request.user)
        context.update({"view": self.__class__.__name__, "perms": self.request.user.get_all_permissions()})
        context.update(self.add_to_context)
        return context

    def get_template_names(self):
        if self.is_ajax: self.template_name = self.template_name or tplx(self.app_label, self.model_name, str(self.__class__.__name__).lower())
        else: self.template_name = self.template_name or tpl(self.app_label, self.model_name, str(self.__class__.__name__).lower())
        logger("mighty", "info", "template: %s" % self.template_name, self.request.user)
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
        logger("mighty", "info", "template: %s" % self.template_name, self.request.user)
        return self.template_name
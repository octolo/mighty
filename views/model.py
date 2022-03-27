from mighty.views.base import BaseView
from mighty.apps import MightyConfig as conf
from mighty.functions import get_logger, tpl

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
        self._logger.info("template: %s" % self.template_name, self.request.user)
        return self.template_name
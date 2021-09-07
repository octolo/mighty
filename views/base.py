from django.contrib.auth.mixins import PermissionRequiredMixin
from mighty.functions import tpl, tplx, get_logger

class BaseView(PermissionRequiredMixin):
    app_label = None
    model_name = None
    template_name = None
    no_permission = False
    is_ajax = False
    permission_required = ()
    add_to_context = {}
    _logger = get_logger()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._logger.info("view: %s" % self.__class__.__name__, extra={'user': self.request.user})
        context.update({"view": self.__class__.__name__, "perms": self.request.user.get_all_permissions()})
        context.update(self.add_to_context)
        return context

    def get_template_names(self):
        if self.is_ajax: self.template_name = self.template_name or tplx(self.app_label, self.model_name, str(self.__class__.__name__).lower())
        else: self.template_name = self.template_name or tpl(self.app_label, self.model_name, str(self.__class__.__name__).lower())
        self._logger.debug("template: %s" % self.template_name, extra={'user': self.request.user, 'log_in_db': self.request.user})
        return self.template_name
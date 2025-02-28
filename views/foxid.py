from mighty.filters import FiltersManager, Foxid
from mighty.views.model import ModelView


class FoxidView(ModelView):
    cache_manager = None
    filters = []
    mandatories = ()

    @property
    def check_mandatories(self):
        return True

    def foxid(self, queryset):
        if self.check_mandatories:
            return Foxid(queryset, self.request, f=self.manager.flts).ready()
        return PermissionDenied()

    @property
    def manager(self):
        self.cache_manager = self.cache_manager or FiltersManager(
            flts=self.filters, mandatories=self.mandatories
        )
        return self.cache_manager

    def get_object(self):
        return self.foxid(super().get_queryset()).get(
            *self.manager.params(self.request)
        )

    def get_queryset(self, queryset=None):
        return self.foxid(super().get_queryset()).filter(
            *self.manager.params(self.request)
        )

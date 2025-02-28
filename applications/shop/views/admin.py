from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mighty.models import Subscription
from mighty.views import ExportView, TemplateView


@method_decorator(login_required, name='dispatch')
class ShopExports(TemplateView):
    template_name = 'admin/shop_exports.html'


@method_decorator(login_required, name='dispatch')
class ShopExport(ExportView):
    model = Subscription
    queryset = Subscription.objects.all()
    fields = ['group', 'amount']

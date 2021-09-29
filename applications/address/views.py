from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from mighty.views import TemplateView, FormDescView
from mighty.applications.address import get_address_backend
from mighty.applications.address.forms import AddressFormDesc
address_backend = get_address_backend()

class AddresFormDescView(FormDescView):
    form = AddressFormDesc

@method_decorator(login_required, name='dispatch')
class LocationDetail(TemplateView):
    @property
    def location(self):
        input_str = self.request.GET.get('location')
        return address_backend.get_location(input_str) if input_str else {}

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.location, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class LocationList(TemplateView):
    @property
    def locations(self):
        input_str = self.request.GET.get('location')
        return address_backend.give_list(input_str) if input_str else []

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(self.locations, safe=False, **response_kwargs)

if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import RetrieveAPIView, ListAPIView
    from rest_framework.response import Response

    class LocationDetail(RetrieveAPIView):
        def get_object(self, queryset=None):
            input_str = self.request.GET.get('location')
            return address_backend.get_list(input_str) if input_str else {}

        def get(self, request, uid, action=None, format=None):
            return Response(self.get_object())

    class LocationList(ListAPIView):
        def get_queryset(self, queryset=None):
            input_str = self.request.GET.get('location')
            return address_backend.give_list(input_str) if input_str else []
    
        def get(self, request, format=None):
            return Response(self.get_queryset())


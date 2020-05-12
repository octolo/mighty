from mighty.views import DetailView, FormView
from mighty.views.viewsets import ModelViewSet, ApiModelViewSet
from mighty.models.applications.user import User
from mighty.applications.user import translates as _, serializers, filters

from django.conf import settings

is_ajax = True if 'rest_framework' in settings.INSTALLED_APPS else False

class UserProfile(DetailView):
    model = User
    #label = "mighty"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"meta": {"title": _.profil}})
        return context

class UserViewSet(ModelViewSet):
    model = User
    is_ajax = is_ajax
    slug = '<uuid:uid>'
    slug_field = "uid"
    slug_url_kwarg = "uid"
    fields = ['username',]

    def __init__(self):
        super().__init__()
        self.add_view('profile', UserProfile, 'profile/')

class UserApiViewSet(ApiModelViewSet):
    model = User
    slug = '<uuid:uid>'
    slug_field = "uid"
    slug_url_kwarg = "uid"
    lookup_field = "uid"
    serializer_class = serializers.UserSerializer
    filter_model = filters.UserFilter
from mighty.views import DetailView, FormView
from mighty.views.viewsets import ModelViewSet, ApiModelViewSet
from mighty.models.applications.user import User
from mighty.applications.user import translates as _, serializers, filters

class UserMe(DetailView):
    over_no_permission = True
    over_is_ajax = False
    model = User
    label = "mighty"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"meta": {"title": _.profil}})
        return context

class UserViewSet(ModelViewSet):
    model = User
    slug = '<uuid:uid>'
    slug_field = "uid"
    slug_url_kwarg = "uid"
    list_is_ajax = True

    def __init__(self):
        super().__init__()
        self.add_view('me', UserMe, 'me/')

class UserApiViewSet(ApiModelViewSet):
    model = User
    slug = '<uuid:uid>'
    slug_field = "uid"
    slug_url_kwarg = "uid"
    lookup_field = "uid"
    serializer_class = serializers.UserSerializer
    filter_model = filters.UserFilter
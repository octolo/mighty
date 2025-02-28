from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from mighty.applications.user import fields
from mighty.applications.user.apps import UserConfig
from mighty.views import DetailView

UserModel = get_user_model()


class ProfileBaseView:
    model = UserModel

    def get_object(self, queryset=None):
        user = self.request.user
        self.request.GET.get('use', UserConfig.Field.style[0])
        # if newstyle != user.style:
        #    user.style = newstyle
        #    user.save()
        newlang = self.request.GET.get('lang')
        if newlang != user.language_pref:
            try:
                from mighty.models import Nationality
                newlang = Nationality.objects.get(alpha2__icontains=newlang)
                user.language = newlang
                user.save()
            except Exception:
                pass
        return user

    def get_fields(self):
        user = self.get_object()
        user_data = {
            'uid': str(user.uid),
            'email': user.email,
            'phone': user.phone,
        }
        user_data.update({field: getattr(user, field) for field in fields.profile})
        if hasattr(user, 'current_tenant') and user.current_tenant:
            user_data.update({'current_tenant': user.current_tenant.uid})
        return user_data


@method_decorator(login_required, name='dispatch')
class ProfileView(ProfileBaseView, DetailView):
    def get_context_data(self, **kwargs):
        return self.get_fields()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)


if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import RetrieveAPIView
    from rest_framework.response import Response

    class ProfileView(ProfileBaseView, RetrieveAPIView):
        def get(self, request, format=None):
            return Response(self.get_fields())

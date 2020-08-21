from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from mighty.applications.user.forms import UserCreationForm
from mighty.applications.user.apps import UserConfig

from mighty.views import DetailView, FormView, CreateView

UserModel = get_user_model()

class UserStyle(DetailView):
    model = UserModel

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        user = self.get_object()
        use = self.request.GET.get('use', UserConfig.Field.style[0])
        use = use if use in UserConfig.Field.style else UserConfig.Field.style[0]
        if use != self.request.user.style:
            self.request.user.style = use
            self.request.user.save()
        return { 'availables': UserConfig.Field.style, 'use': use }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)


from rest_framework.views import APIView
from rest_framework.response import Response
from mighty.applications.user.serializers import UserSerializer
class APIMyDetail(APIView):

    def get(self, request, format=None):
        serializer = UserSerializer(UserModel.objects.all().first())
        return Response(serializer.data)
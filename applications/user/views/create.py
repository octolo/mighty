from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from mighty.applications.user.forms import UserCreationForm
from mighty.views import AddView

UserModel = get_user_model()


class CreateUserView(AddView):
    form_class = UserCreationForm
    template_name = 'mighty/form.html'
    model = UserModel

    def get_success_url(self):
        return reverse('generic-success')


if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import CreateAPIView

    from mighty.applications.user.serializers import CreateUserSerializer

    class CreateUserView(CreateAPIView):
        permission_classes = ()
        serializer_class = CreateUserSerializer
        model = UserModel

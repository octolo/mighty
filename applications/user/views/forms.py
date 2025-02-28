from mighty.applications.user.forms import UserCreationForm
from mighty.views.form import FormDescView


class CreatUserFormView(FormDescView):
    form = UserCreationForm

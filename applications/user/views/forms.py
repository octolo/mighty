from mighty.views.form import FormDescView
from mighty.applications.user.forms import UserCreationForm

class CreatUserFormView(FormDescView):
    form = UserCreationForm

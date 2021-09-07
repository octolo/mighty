from django.views.generic.edit import FormView
from mighty.views.base import BaseView

class FormView(BaseView, FormView):
    pass


class FormConfigView(FormView):
    pass

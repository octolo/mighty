from django.db.models import Q
from mighty.views.viewsets import ModelViewSet
from mighty.views import ListView, DetailView
from tenant.models import Tenant, Invitation

class TenantList(ListView):
    def get_queryset(self):
        return Roles.objectsB.filter(user=self.request.user)

class TenantViewSet(ModelViewSet):
    model = Tenant

    def __init__(self):
        super().__init__()
        self.add_view('list', TenantList, '')

class InvitationList(ListView):
    def get_queryset(self):
        return Invitation.objectsB.filter(Q(user=self.request.user)|Q(by=self.request.user))

class InvitationDetail(DetailView):
    def get_object(self):
        return Invitation.objectsB.get(Q(user=self.request.user)|Q(by=self.request.user))

class InvitaionViewSet(ModelViewSet):
    model = Invitation
    
    def __init__(self):
        super().__init__()
        self.add_view('list', InvitationList, '')
        self.add_view('detail', InvitationDetail, '')
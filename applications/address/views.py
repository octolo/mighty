from django.shortcuts import render
from mighty.views.viewsets import ModelViewSet
from mighty.models.applications.address import Address

class AddressViewSet(ModelViewSet):
    slug = '<str:uid>'
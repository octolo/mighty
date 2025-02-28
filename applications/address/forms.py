from django import forms

from mighty.applications.address import translates as _
from mighty.forms import FormDescriptable


class AddressFormDesc(FormDescriptable):
    address = forms.CharField(label=_.address, max_length=255)
    locality = forms.CharField(label=_.locality, max_length=255)
    postal_code = forms.CharField(label=_.postal_code, max_length=255, required=False)
    state = forms.CharField(label=_.state, max_length=255, required=False)
    state_code = forms.CharField(label=_.state_code, max_length=255, required=False)
    country = forms.CharField(label=_.country, max_length=255, required=False)
    cedex = forms.CharField(label=_.cedex, max_length=255, required=False)
    cedex_code = forms.CharField(label=_.cedex_code, max_length=255, required=False)
    special = forms.CharField(label=_.special, max_length=255, required=False)
    index = forms.CharField(label=_.index, max_length=255, required=False)
    complement = forms.CharField(label=_.complement, max_length=255, required=False)

# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import CartridgeType

class AddItems(forms.Form):
    cart_name = forms.CharField(label=_('name consumables'), max_length=256)
    cart_type = forms.ModelChoiceField(queryset=CartridgeType.objects.all(), empty_label=None)
    cart_count = forms.IntegerField()
    cart_new = forms.BooleanField()

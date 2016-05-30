# -*- coding:utf-8 -*-

from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from index.models import City


class CityF(ModelForm):
    class Meta:
        model = City
        fields = ['city_name']

    required_css_class = 'required'

    def clean_city_name(self):
        """проверяем город на наличие дублей.
        """
        data = self.cleaned_data.get('city_name').strip()
        search_type = City.objects.filter(city_name__iexact=data)
        if search_type:
            raise forms.ValidationError(_('This city already exists!'))            
        else:
            return data

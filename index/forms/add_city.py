# -*- coding:utf-8 -*-

from django.forms import ModelForm
from index.models import City


class CityF(ModelForm):
    class Meta:
        model = City
        fields = ['city_name']

    required_css_class = 'required'

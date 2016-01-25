# -*- coding:utf-8 -*-

from django import forms

class DateForm(forms.Form):
#    start_date = forms.CharField()
#    end_date   = forms.CharField()
#    start_date = forms.DateField(widget=forms.DateInput(format = '%Y/%m/%d'))
#    end_date   = forms.DateField(widget=forms.DateInput(format = '%Y/%m/%d'))
    start_date = forms.DateField()
    end_date   = forms.DateField()
    #http://stackoverflow.com/questions/5449604/django-calendar-widget-in-a-custom-form


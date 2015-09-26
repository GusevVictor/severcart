from django.forms import ModelForm
from index.models import FirmTonerRefill
from django import forms


class FirmTonerRefillF(ModelForm):
    class Meta:
        model = FirmTonerRefill
        fields = ['firm_name', 'firm_city', 'firm_contacts', 'firm_address', 'firm_comments']

        widgets = {
            'firm_contacts': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'firm_address': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'firm_comments': forms.Textarea(attrs={'rows': 2, 'cols': 15}),
        }

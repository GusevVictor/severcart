from django import forms
from django.utils.translation import ugettext_lazy as _
from index.models import CartridgeItemName, CartridgeType

class EditName(forms.Form):
    cartName = forms.CharField(required=True, label=_('Name'))
    
    cartType = forms.ModelChoiceField(queryset=CartridgeType.objects.all(), required=True, label=_('Type'))

    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': 15, 'rows': 30}), required=False, label=_('Comment'))

    required_css_class = 'required'

    def clean_cartName(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('cartName', '').strip():
            raise forms.ValidationError(_('Required field'))
        return self.cleaned_data.get('cartName').strip()

    def clean_cartType(self):
        """
        """
        if not self.cleaned_data.get('cartType', ''):
            raise forms.ValidationError(_('Required field'))
        return self.cleaned_data.get('cartType')

    def clean_comment(self):
        """Проверяем, что длина комментария не превышает допустимой длины.
        """
        if len(self.cleaned_data['comment']) > 161:
            raise forms.ValidationError(_('You have exceeded the maximum number of characters. No more than 160.'))
        return self.cleaned_data['comment'].strip()

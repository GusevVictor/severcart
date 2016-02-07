from django import forms
#from django.core.exceptions import ValidationError
from index.models import CartridgeItemName, CartridgeType

class EditName(forms.Form):
    cartName = forms.CharField(required=True, label='Название')
    
    cartType = forms.ModelChoiceField(queryset=CartridgeType.objects.all(), required=True, label='Тип')

    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': 15, 'rows': 30}), required=False, label='Комментарий')

    required_css_class = 'required'

    def clean_cartName(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('cartName', '').strip():
            raise forms.ValidationError('Поле обязательно для заполнения.')
        return self.cleaned_data.get('cartName').strip()

    def clean_cartType(self):
        """
        """
        if not self.cleaned_data.get('cartType', ''):
            raise forms.ValidationError('Поле обязательно для заполнения.')
        return self.cleaned_data.get('cartType')

    def clean_comment(self):
        """Проверяем, что длина комментария не превышает допустимой длины.
        """
        if len(self.cleaned_data['comment']) > 161:
            raise forms.ValidationError('Превышено максимальное количество символов. Допустимо не более 160.')
        return self.cleaned_data['comment'].strip()

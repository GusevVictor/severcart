from django import forms
from django.core.exceptions import ValidationError
from index.models import CartridgeItemName

class AddItems(forms.Form):
    cartName = forms.ModelChoiceField(queryset=CartridgeItemName.objects.all(),
                                      error_messages={'required': 'Поле обязательно для заполнения.'},
                                      empty_label=' ',
                                      required=True,
                                      )
    cartCount = forms.CharField(  max_length = 4,
                                  widget=forms.TextInput(attrs={'class': 'pm_counter', 'readonly': 'readonly'}),
                                  error_messages={'required': 'Поле обязательно для заполнения.'},
                                  required=True,
                                )

    required_css_class = 'required'

    def clean_cartName(self):
        """
        Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('cartName', ''):
            raise ValidationError("Поле обязательно для заполнения.")
        return self.cleaned_data.get('cartName', '')

    def clean_cartCount(self):
        """

        """
        temp_count = self.cleaned_data.get('cartCount', '')
        try:
            temp_count = int(temp_count)
        except ValueError:
            raise ValidationError("Вы ввели ошибочные данные.")

        if temp_count <= 0:
            raise ValidationError("Значение должно быть больше нуля.")

        if not temp_count:
            raise ValidationError("Поле не может быть пустым.")

        return self.cleaned_data.get('cartCount', '')

from django import forms
from django.core.exceptions import ValidationError
from index.models import FirmTonerRefill

class AddDoc(forms.Form):
    number   = forms.CharField(max_length = 16, label='Номер', required=True)

    title   = forms.CharField(max_length = 256, label='Название', required=True)

    firm = forms.ModelChoiceField(queryset=FirmTonerRefill.objects.all(),
                                  error_messages={'required': 'Поле обязательно для заполнения.'},
                                  label='Фирма поставщик',
                                  required=True,
                                  )
    
    short_cont = forms.CharField(max_length = 256, label='Краткое содержимое', required=False)

    money = forms.CharField(required=False)
    
    #widget=forms.TextInput(attrs={'class': 'pm_counter', 'readonly': 'readonly'}),
    
    #required_css_class = 'required'

    def clean_number(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('number', ''):
            raise ValidationError("Поле обязательно для заполнения.")
        return self.cleaned_data.get('number', '')

    def clean_money(self):
        """Проверяет на корректность введённую сумму.
        """
        temp_count = self.cleaned_data.get('money', '')
        try:
            temp_count = int(temp_count)
        except ValueError:
            raise ValidationError("Вы ввели ошибочные данные.")

        if temp_count <= 0:
            raise ValidationError("Значение должно быть больше нуля.")

        if not temp_count:
            raise ValidationError("Поле не может быть пустым.")

        return self.cleaned_data.get('money', '')


    def clean_title(self):
        """
        """
        if not self.cleaned_data.get('title', ''):
            raise ValidationError('Поле обязательно для заполнения.')
        return self.cleaned_data.get('title', '')

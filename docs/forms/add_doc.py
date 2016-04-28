import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from index.models import FirmTonerRefill
from events.forms import del_leding_zero

class AddDoc(forms.Form):
    number = forms.CharField(max_length=64, label=_('Number'), required=True)

    title  = forms.CharField(max_length=256, label=_('Name'), required=True)

    firm   = forms.ModelChoiceField(queryset=FirmTonerRefill.objects.all(),
                                  error_messages={'required': _('Required field.')},
                                  label=_('Firm supplier'),
                                  required=True,
                                  )
    
    short_cont = forms.CharField(max_length=256, label=_('Summary'), required=False, widget=forms.widgets.Textarea())

    money = forms.CharField(required=False)
    
    date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}))

    DOC_TYPE = (
        ('', ''),
        (1, _('Delivery agreement')),
        (2, _('Service agreement')),
    )

    doc_type = forms.ChoiceField(choices=DOC_TYPE)

    def clean_number(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('number', ''):
            raise ValidationError(_('Required field.'))
        return self.cleaned_data.get('number', '').strip()

    def clean_money(self):
        """Проверяет на корректность введённую сумму.
        """
        money = self.cleaned_data.get('money', '')
        if money == '':
            return None
        
        if ',' in money:
            money = money.split(',')
        elif '.' in money:
            money = money.split('.')
        else:
            money = [money]    
        try:
            money = [ int(i) for i in money ]
        except ValueError:
            raise ValidationError(_('You have entered wrong amount'))
        else:
            # преобразуем сумму в копейки/центы/евроценты
            if len(money) == 1:
                return (money[0] * 100)
            elif len(money) == 2:
                return (money[0] * 100) + money[1]
            else:
                raise ValidationError(_('You have entered wrong amount'))

    def clean_title(self):
        """
        """
        if not self.cleaned_data.get('title', ''):
            raise ValidationError(_('Required field.'))
        return self.cleaned_data.get('title', '').strip()

    def clean_short_cont(self):
        """
        """
        return self.cleaned_data.get('short_cont', '').strip()

    def clean_date(self):
        """Проверяем на корректность 1 поле с данными.
        """
        if not(self.cleaned_data.get('date', '')):
            return None
        else:
            prepare_list = self.cleaned_data.get('date').split(r'/')
            if len(prepare_list) == 3:
                # если пользователь не смухлевал, то кол-во элементов = 3
                date_value  = prepare_list[0]
                date_value  = del_leding_zero(date_value)
                month_value = prepare_list[1]
                month_value = del_leding_zero(month_value)
                year_value  = prepare_list[2]
                year_value  = int(year_value)
                date = datetime.datetime(year_value, month_value, date_value)
                return date
            else:
                return None


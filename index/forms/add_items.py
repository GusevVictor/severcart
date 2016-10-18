# -*- coding:utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from index.models import CartridgeItemName
from index.helpers import str2int
from docs.models  import SCDoc
from storages.models import Storages
from common.helpers import del_leding_zero


TIME = (
    (22, '11:00'),
    (0, '00:00'),
    (1, '00:30'),
    (2, '01:00'),
    (3, '01:30'),
    (4, '02:00'),
    (5, '02:30'),
    (6, '03:00'),
    (7, '03:30'),
    (8, '04:00'),
    (9, '04:30'),
    (10, '05:00'),
    (11, '05:30'),
    (12, '06:00'),
    (13, '06:30'),
    (14, '07:00'),
    (15, '07:30'),
    (16, '08:00'),
    (17, '08:30'),
    (18, '09:00'),
    (19, '09:30'),
    (20, '10:00'),
    (21, '10:30'),
    (23, '11:30'),
    (24, '12:00'),
    (25, '12:30'),
    (26, '13:00'),
    (27, '13:30'),
    (28, '14:00'),
    (29, '14:30'),
    (30, '15:00'),
    (31, '15:30'),
    (32, '16:00'),
    (33, '16:30'),
    (34, '17:00'),
    (35, '17:30'),
    (36, '18:00'),
    (37, '18:30'),
    (38, '19:00'),
    (39, '19:30'),
    (40, '20:00'),
    (41, '20:30'),
    (42, '21:00'),
    (43, '21:30'),
    (44, '22:00'),
    (45, '22:30'),
    (46, '23:00'),
    (47, '23:30'),
)

class AddItems(forms.Form):
    manualNumber = forms.CharField(max_length = 256, required=False)
    cartName = forms.ModelChoiceField(queryset=CartridgeItemName.objects.all(),
                                      error_messages={'required': _('Required field.')},
                                      empty_label=' ',
                                      required=True,
                                      )
    
    doc = forms.ModelChoiceField(queryset=SCDoc.objects.filter(), required=False)
    storages = forms.ModelChoiceField(queryset=Storages.objects.filter(), label=_('Storage'))
    cartCount = forms.CharField(max_length = 4,
                                widget=forms.TextInput(attrs={'class': 'pm_counter', 'readonly': 'readonly'}),
                                error_messages={'required': _('Required field.')},
                                required=True
                                )


    set_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}))
    
    time = forms.ChoiceField(choices=TIME, required=False)

    required_css_class = 'required'

    def clean_cartName(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('cartName', ''):
            raise ValidationError(_('Required field.'))
        return self.cleaned_data.get('cartName', '')

    def clean_cartCount(self):
        """
        """
        temp_count = self.cleaned_data.get('cartCount', '')
        try:
            temp_count = int(temp_count)
        except ValueError:
            raise ValidationError(_('You have entered the wrong data.'))

        if temp_count <= 0:
            raise ValidationError(_('The value must be greater than zero.'))

        if not temp_count:
            raise ValidationError(_('Required field.'))

        return self.cleaned_data.get('cartCount', '')

    def clean_doc(self):
        """
        """
        if not self.cleaned_data.get('doc', 0):
            return 0
        
        doc_id = self.cleaned_data.get('doc')
        return doc_id.pk

    def clean_storages(self):
        """
        """
        if not self.cleaned_data.get('storages', 0):
            raise ValidationError(_('Required field.'))
        
        return self.cleaned_data.get('storages')

    def clean_time(self):
        """Возвращаем объект(словарь) из часов, минут и секкунд установленных пользователем.
        """
        if not self.cleaned_data.get('time', 0):
            return {'hours': 0, 'minutes': 0, 'seconds': 0}
        
        if self.cleaned_data.get('time') == '':
            return {'hours': 0, 'minutes': 0, 'seconds': 0}

        time_digit = self.cleaned_data.get('time')
        
        try:
            time_digit = int(time_digit)
        except:
            return {'hours': 0, 'minutes': 0, 'seconds': 0}
        for times in TIME:
            if times[0] == time_digit:
                time = times[1].split(':')
                time = {'hours': int(time[0]), 'minutes': int(time[1]), 'seconds': 0}
                break

        return time

    def clean_set_date(self):
        """Возвращает словарь из дни, месяцы, годы.
           По-умолчанию возвращаем время с эпохи начала UNIX, если в входных данных ошибки.
        """
        if not self.cleaned_data.get('set_date', 0):
            return {'day': 1, 'month': 1, 'year': 1970}

        prepare_list = self.cleaned_data.get('set_date').split(r'/')
        if len(prepare_list) == 3:
            # если пользователь не смухлевал, то кол-во элементов = 3
            date_value  = prepare_list[0]
            date_value  = del_leding_zero(date_value)
            month_value = prepare_list[1]
            month_value = del_leding_zero(month_value)
            year_value  = prepare_list[2]
            year_value  = str2int(year_value) 
            return {'day': date_value, 'month': month_value, 'year': year_value}
        else:
            return {'day': 1, 'month': 1, 'year': 1970}

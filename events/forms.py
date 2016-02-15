# -*- coding:utf-8 -*-

from django import forms

def del_leding_zero(data):
    """Убираем лидирующий ноль, если он есть.
    """
    if data[0] == '0':
        return int(data[1:])
    else:
        return int(data)

class DateForm(forms.Form):
    #http://stackoverflow.com/questions/16356289/how-to-show-datepicker-calender-on-datefield#16356818
    start_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}))
    end_date   = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}))

    def clean_start_date(self):
        """Проверяем на корректность 1 поле с данными.
        """
        if not(self.cleaned_data.get('start_date', '')):
            return None
        else:
            prepare_list = self.cleaned_data.get('start_date').split(r'/')
            if len(prepare_list) == 3:
                # если пользователь не смухлевал, то кол-во элементов = 3
                date_value  = prepare_list[0]
                date_value  = del_leding_zero(date_value)
                month_value = prepare_list[1]
                month_value = del_leding_zero(month_value)
                year_value  = prepare_list[2]
                return {'date_value': date_value, 'month_value': month_value, 'year_value': year_value}
            else:
                return None

    def clean_end_date(self):
        """Проверяем на корректность 2 поле с данными.
        """
        if not(self.cleaned_data.get('end_date', '')):
            return None
        else:
            prepare_list = self.cleaned_data.get('end_date').split(r'/')
            if len(prepare_list) == 3:
                # если пользователь не смухлевал, то кол-во элементов = 3
                date_value  = prepare_list[0]
                date_value  = del_leding_zero(date_value)
                month_value = prepare_list[1]
                month_value = del_leding_zero(month_value)
                year_value  = prepare_list[2]
                return {'date_value': int(date_value), 'month_value': int(month_value), 'year_value': int(year_value)}
            else:
                return None

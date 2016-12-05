# -*- coding:utf-8 -*-

import datetime, pytz
from django import forms
from django.utils.translation import ugettext_lazy as _
from index.models import OrganizationUnits
from index.helpers import str2int
from django.core.exceptions import ValidationError
from service.helpers import SevercartConfigs


class NoUse(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes())
    
    OPTIONS = ((10, '10'), (20, '20'), (0, _('All over the past year')))
    
    diap = forms.ChoiceField(choices=OPTIONS)

    def clean_org(self):
        """
        """
        if not self.cleaned_data.get('org', ''):
            raise ValidationError(_('Required field.'))
        
        return self.cleaned_data.get('org', '')
  
    def clean_diap(self):
        """
        """
        diap_post = self.cleaned_data.get('diap', ''
            )
        if not diap_post:
            raise ValidationError(_('Required field.'))
        
        diap_post = int(diap_post)        
        if not(diap_post == 10 or diap_post == 20 or diap_post == 0):
            raise ValidationError(_('Transferred to invalid values.'))
        
        return diap_post

class Amortizing(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes())

    cont = forms.CharField(max_length = 4, widget=forms.TextInput(attrs={'class': 'pm_counter', 
                                                                        'readonly': 'readonly',
                                                                        'data': '1'}))

    def clean_cont(self):
        """
        """
        temp_count = self.cleaned_data.get('cont', '')
        try:
            temp_count = int(temp_count)
        except ValueError:
            raise ValidationError(_('You have entered incorrect data.'))
        if temp_count <= 0:
            raise ValidationError(_('The value must be greater than zero.'))
        if not temp_count:
            raise ValidationError(_('Field cannot be empty.'))
        return self.cleaned_data.get('cont', '')

    def clean_org(self):
        """
        """
        if not self.cleaned_data.get('org', ''):
            raise ValidationError(_('Required field.'))
        return self.cleaned_data.get('org', '')

class UsersCartridges(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes(), 
                                required=True, 
                                label=_('Departament'), 
                                widget=forms.Select(attrs={'class':'select_root_org'}))

    unit = forms.ModelChoiceField(queryset=OrganizationUnits.objects.all(), 
                                 required=False, 
                                 label=_('Organization unit'),
                                 widget=forms.Select(attrs={'class':'select_org_unit'}))

    start_date = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}), label=_('Start date'))

    end_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}), label=_('End date'))

    required_css_class = 'required'

    def clean_start_date(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('start_date', ''):
            raise ValidationError(_('Required field.'))

        start_date = self.cleaned_data.get('start_date', '').strip()
        start_date = start_date.split(r'/')
        conf = SevercartConfigs()
        if len(start_date) == 3:
            # если пользователь не смухлевал, то кол-во элементов = 3
            date_value  = start_date[0]
            month_value = start_date[1]
            year_value = start_date[2]
            date_value = str2int(date_value)
            month_value = str2int(month_value)
            year_value = str2int(year_value)
            gte_date = datetime.datetime(year=year_value, 
                        month=month_value, 
                        day=date_value, 
                        hour=0,
                        minute=0,
                        microsecond=0,
                        tzinfo=pytz.timezone(conf.time_zone)
                        )
        else:
            raise ValidationError(_('Error in start date.'))
        return gte_date

    def clean_end_date(self):
        """Проверят на пустоту введенные данные.
        """
        # проверяем на корректность дату окончания просмотра списка
        end_date = self.cleaned_data.get('end_date', '').strip()
        end_date = end_date.split(r'/')
        conf = SevercartConfigs()
        if  end_date and len(end_date) == 3:
            # если пользователь не смухлевал, то кол-во элементов = 3
            date_value  = end_date[0]
            #date_value  = del_leding_zero(date_value)
            month_value = end_date[1]
            #month_value = del_leding_zero(month_value)
            year_value  = end_date[2]
            #lte_date    = '%s-%s-%s 23:59:59' % (year_value, month_value, date_value,)
            date_value = str2int(date_value)
            month_value = str2int(month_value)
            year_value = str2int(year_value)
            
            lte_date = datetime.datetime(year=year_value, 
                        month=month_value, 
                        day=date_value, 
                        hour=23,
                        minute=59,
                        microsecond=999,
                        tzinfo=pytz.timezone(conf.time_zone)
                        )
        else:
            return False
        return lte_date


class UseProducts(forms.Form):
    org = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes(), label=_('Organization unit'))

    start_date = forms.CharField(widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}), label=_('Start date'))

    end_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}), label=_('End date'))

    required_css_class = 'required'

    def clean_org(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('org', ''):
            raise ValidationError(_('Required field.'))
        org = self.cleaned_data.get('org')
        org = org.pk
        try:
            org = int(org)
        except ValueError:
            org = 0
        return org

    def clean_start_date(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('start_date', ''):
            raise ValidationError(_('Required field.'))

        start_date = self.cleaned_data.get('start_date', '').strip()
        start_date = start_date.split(r'/')

        if len(start_date) == 3:
            # если пользователь не смухлевал, то кол-во элементов = 3
            date_value  = start_date[0]
            month_value = start_date[1]
            year_value  = start_date[2]
            gte_date    = '%s-%s-%s 00:00:00' % (year_value, month_value, date_value,)
        else:
            raise ValidationError(_('Error in start date.'))
        return gte_date

    def clean_end_date(self):
        """Проверят на пустоту введенные данные.
        """
        # проверяем на корректность дату окончания просмотра списка
        end_date = self.cleaned_data.get('end_date', '').strip()
        end_date = end_date.split(r'/')
        
        if  end_date and len(end_date) == 3:
            # если пользователь не смухлевал, то кол-во элементов = 3
            date_value  = end_date[0]
            #date_value  = del_leding_zero(date_value)
            month_value = end_date[1]
            #month_value = del_leding_zero(month_value)
            year_value  = end_date[2]
            lte_date    = '%s-%s-%s 23:59:59' % (year_value, month_value, date_value,)
        else:
            return False
        return lte_date

class Firms(forms.Form):
    start_date = forms.CharField(widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}), label=_('Start date'))

    end_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'datepicker', 'readonly':'readonly'}), label=_('End date'))

    def clean_start_date(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('start_date', ''):
            raise ValidationError(_('Required field.'))

        start_date = self.cleaned_data.get('start_date', '').strip()
        start_date = start_date.split(r'/')

        if len(start_date) == 3:
            # если пользователь не смухлевал, то кол-во элементов = 3
            date_value  = start_date[0]
            month_value = start_date[1]
            year_value = start_date[2]
            date_value = str2int(date_value)
            month_value = str2int(month_value)
            year_value = str2int(year_value)
            gte_date = datetime.datetime(year=year_value, 
                        month=month_value, 
                        day=date_value, 
                        )
        else:
            raise ValidationError(_('Error in start date.'))
        return gte_date

    def clean_end_date(self):
        """Проверят на пустоту введенные данные.
        """
        # проверяем на корректность дату окончания просмотра списка
        end_date = self.cleaned_data.get('end_date', '').strip()
        end_date = end_date.split(r'/')
        if  end_date and len(end_date) == 3:
            # если пользователь не смухлевал, то кол-во элементов = 3
            date_value  = end_date[0]
            #date_value  = del_leding_zero(date_value)
            month_value = end_date[1]
            #month_value = del_leding_zero(month_value)
            year_value  = end_date[2]
            #lte_date    = '%s-%s-%s 23:59:59' % (year_value, month_value, date_value,)
            date_value = str2int(date_value)
            month_value = str2int(month_value)
            year_value = str2int(year_value)
            
            lte_date = datetime.datetime(year=year_value, 
                        month=month_value, 
                        day=date_value, 
                        )
        else:
            return False
        return lte_date

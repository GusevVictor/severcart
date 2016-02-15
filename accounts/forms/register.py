# -*- coding:utf-8 -*-

from django import forms
from accounts.models import AnconUser
from django.utils.translation import ugettext_lazy as _
from index.models import OrganizationUnits

class RegistrationForm(forms.ModelForm):
    """Form for registering a new account.
    """
    username = forms.CharField(widget=forms.TextInput, label=_('Login'))
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label=_('Password'))
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label=_('Password again'))

    required_css_class = 'required'

    departament = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes(),
                                      error_messages={'required': _('Required field')},
                                      empty_label=' ',
                                      required=True,
                                      label = _('Organization unit'),
                                      )

    is_admin = forms.BooleanField(required=False, label=_('Administrator?'))

    class Meta:
        model = AnconUser
        fields = ['username', 'password1', 'password2', 'fio', 'email','departament', 'is_admin']

    def clean(self):
        """Verifies that the values entered into the password fields match
        """
        # вызывает ошибку дублирования логина
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('Passwords do not match. Please enter them again'))
        return self.cleaned_data

    def save(self, commit=True):
        username   = self.cleaned_data['username']
        password1  = self.cleaned_data['password1']
        fio        = self.cleaned_data['fio']
        is_admin   = self.cleaned_data['is_admin']
        departament = self.cleaned_data['departament']
        
        user = AnconUser.objects.filter(username=username)
        # проверяем есть ли уже пользователь с таким логином
        if user:
            #user.set_password(self.cleaned_data['password1'])
            user.update(fio=fio, departament=departament)
            #user.save()
        else:
            user = super(RegistrationForm, self).save(commit)
            user.set_password(self.cleaned_data['password1'])
            if commit:
                user.save()
        return user

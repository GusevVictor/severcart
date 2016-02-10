# -*- coding:utf-8 -*-

from django import forms
from accounts.models import AnconUser
from index.models import OrganizationUnits

class RegistrationForm(forms.ModelForm):
    """Form for registering a new account.
    """
    username = forms.CharField(widget=forms.TextInput, label="Логин")
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Повторите пароль")

    required_css_class = 'required'

    departament = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes(),
                                      error_messages={'required': 'Поле обязательно для заполнения.'},
                                      empty_label=' ',
                                      required=True,
                                      label = 'Организация',
                                      )
    is_admin = forms.BooleanField(required=False, label='Администратор?')

    class Meta:
        model = AnconUser
        fields = ['username', 'password1', 'password2', 'fio', 'departament', 'is_admin']

    def clean(self):
        """
        Verifies that the values entered into the password fields match

        NOTE: Errors here will appear in ``non_field_errors()`` because it applies to more than one field.
        """
        # вызывает ошибку дублирования логина
        #self.cleaned_data = super(RegistrationForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Пароли не совпадают. Введите их повторно.")
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

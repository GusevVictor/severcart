# -*- coding:utf-8 -*-

from django import forms
from accounts.models import AnconUser
from django.utils.translation import ugettext_lazy as _
from index.models import OrganizationUnits

class EditUserForm(forms.Form):
    """Редактирование информации о текущем пользователе.
    """
    user_id    = forms.CharField(widget=forms.HiddenInput(), required=True)
    username   = forms.CharField(widget=forms.TextInput(attrs={'readonly': True}), label=_('Login'), required=True)
    fio        = forms.CharField(label=_('Full name'), required=False)
    email      = forms.EmailField(required=False)
    required_css_class = 'required'

    departament = forms.ModelChoiceField(queryset=OrganizationUnits.objects.root_nodes(),
                                      error_messages={'required': _('Required field')},
                                      empty_label=' ',
                                      required=True,
                                      label = _('Organization'),
                                      )

    is_admin = forms.BooleanField(required=False, label=_('Administrator?'))

    def user_id_clean(self):
        uid = self.cleaned_data['user_id']
        try:
            uid = int(uid) 
        except:
            raise forms.ValidationError(_('Error in !'))
        else:
            return uid


    def save(self):
        user_id          = self.cleaned_data['user_id']
        username         = self.cleaned_data['username']
        fio              = self.cleaned_data['fio']
        is_admin         = self.cleaned_data['is_admin']
        email            = self.cleaned_data['email']
        departament      = self.cleaned_data['departament']

        user             = AnconUser.objects.get(pk=user_id)
        user.fio         = fio
        user.is_admin    = is_admin
        user.email       = email
        user.departament = departament
        user.save()
        return user

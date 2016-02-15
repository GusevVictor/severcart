# -*- coding:utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


class EditCommentForm(forms.Form):
    """Форма добавления, либо редктирования комментария.
    """
    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': 15, 'rows': 30}), 
        label=_('comment'))

    required_css_class = 'required'
    def clean(self):
        """Проверяем, что длина комментария не превышает допустимой длины.
        """
        if len(self.cleaned_data['comment']) > 161:
            raise forms.ValidationError(_('You have exceeded the maximum number of characters. No more than 160.'))
        return self.cleaned_data

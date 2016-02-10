# -*- coding:utf-8 -*-

from django import forms

class EditCommentForm(forms.Form):
    """Форма добавления, либо редктирования комментария.
    """
    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': 15, 'rows': 30}), 
        label="Комментарий")

    required_css_class = 'required'
    def clean(self):
        """Проверяем, что длина комментария не превышает допустимой длины.
        """
        #if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
        #    if self.cleaned_data['password1'] != self.cleaned_data['password2']:
        #        raise forms.ValidationError("Пароли не совпадают. Введите их повторно.")
        if len(self.cleaned_data['comment']) > 161:
            raise forms.ValidationError("Превышено максимальное количество символов. Допустимо не более 160.")
        return self.cleaned_data

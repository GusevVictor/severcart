# -*- coding:utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from index.models import CartridgeItemName, CartridgeItem
from docs.models  import SCDoc
from index.forms.base_add_form import BaseAddForm


class AddItemsFromBarCodeScanner(BaseAddForm):
    """Форма добавления новых/бу РМ на склад с помощью сканера штрихкода
    """
    cartNumber = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'readonly': True, 'class': 'barcode'}), required=True)

    cartName = forms.ModelChoiceField(queryset=CartridgeItemName.objects.all(),
                                      error_messages={'required': _('Required field.')},
                                      empty_label=' ',
                                      required=True,
                                      )
    
    doc = forms.ModelChoiceField(queryset=SCDoc.objects.filter(), required=False)

    tumbler = forms.CharField(required=True)

    required_css_class = 'required'

    def clean_cartNumber(self):
        """Провем на дубли номера РМ.
        """
        cart_number = self.cleaned_data.get('cartNumber', '')
        cart_number = cart_number.strip()
        find_count = CartridgeItem.objects.filter(cart_number=cart_number)
        if len(find_count):
            raise ValidationError(_('The object with number %(cart_number)s is already registered.') % {'cart_number': cart_number})
        else:
            return cart_number

    def clean_cartName(self):
        """Проверят на пустоту введенные данные.
        """
        if not self.cleaned_data.get('cartName', ''):
            raise ValidationError(_('Required field.'))
        return self.cleaned_data.get('cartName', '')

    def clean_doc(self):
        """
        """
        if not self.cleaned_data.get('doc', 0):
            return 0
        
        doc_id = self.cleaned_data.get('doc')
        return doc_id.pk

    def clean_tumbler(self):
        """
        """        
        check = self.cleaned_data.get('tumbler', '0')
        if check == '0':
            return False
        elif check == '1':
            return True
        else:
            return False

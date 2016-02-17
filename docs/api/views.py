# -*- coding:utf-8 -*-

import os, io
import time
import json
from django.http import JsonResponse, HttpResponse
from django.db.models.deletion import ProtectedError
from django.conf import settings
from django.utils.translation import ugettext as _
from docx import Document
from docx.shared import Inches
from index.models import CartridgeItemName, CartridgeType
from index.helpers import check_ajax_auth


import logging
logger = logging.getLogger(__name__)

@check_ajax_auth
def del_cart_name(request):
    """Удаляем имя расходного материала через аякс
    """
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')
    
    resp_dict = dict()
    cart_name_id = request.POST.get('cart_name_id', '')
    atype = request.POST.get('atype', '')

    try:
        cart_name_id = int(cart_name_id)
    except ValueError:
        cart_name_id = 0

    if atype == 'cart_name':
        try:
            m1 = CartridgeItemName.objects.get(pk=cart_name_id)
        except CartridgeItemName.DoesNotExist:
            resp_dict['error'] = '1'
            resp_dict['text']  = _('The object with the ID is not found.')
        try:
            m1.delete()
        except ProtectedError:
            resp_dict['error'] = '1'
            resp_dict['text']  = _('Name can not be removed, ie. other objects reference it.')
        else:
            resp_dict['error'] = '0'
            resp_dict['text']  = _('Name deleted successfully.')
    elif atype == 'cart_type':
        try:
            m1 = CartridgeType.objects.get(pk=cart_name_id)
        except CartridgeType.DoesNotExist:
            resp_dict['error'] = '1'
            resp_dict['text']  = _('The object with the ID is not found.')
        try:
            m1.delete()
        except ProtectedError:
            resp_dict['error'] = '1'
            resp_dict['text']  = _('Type can not be deleted, ie the other sites link to it.')
        else:
            resp_dict['error'] = '0'
            resp_dict['text']  = _('Name deleted successfully.')
    return JsonResponse(resp_dict, safe=False)


@check_ajax_auth
def generate_act(request):
    """Генерация нового docx документа. Вью возвращает Url с свежезгенерированным файлом. 
    """
    from docs.models import SCDoc
    from docs.helpers import group_names

    resp_dict = dict()
    if request.method != 'POST':
        return HttpResponse('<h1>' + _('Only use POST requests!') + '</h1>')    
    
    doc_id = request.POST.get('doc_id', '')
    doc_action = request.POST.get('doc_action', '')

    try:
        doc_id = int(doc_id)
    except ValueError:
        doc_id = 0

    try:
        m1 = SCDoc.objects.get(pk=doc_id)
    except SCDoc.DoesNotExist:
        resp_dict['error'] = '1'
        resp_dict['text']  = _('The object with the ID is not found.')
        return JsonResponse(resp_dict, safe=False)

    jsontext = m1.short_cont
    jsontext = json.loads(jsontext)
    if doc_action == 'docx_with_group':
        file_full_name = os.path.join(settings.MEDIA_ROOT, m1.number + '_1.docx')
        names_counts = group_names(jsontext)
        if names_counts:
            # генерация печатной версии документа
            document = Document()
            table = document.add_table(rows=1, cols=2)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = _('The name of the cartridge')
            hdr_cells[1].text = _('Amount')
            for item in names_counts:
                row_cells = table.add_row().cells
                row_cells[0].text = str(item[0])
                row_cells[1].text = str(item[1])
            document.add_page_break()
            document.save(file_full_name)
            resp_dict['error'] = '0'
            resp_dict['text']  = _('Document %(doc_number)s_1.docx generated') % { 'doc_number': m1.number }
            resp_dict['url'] = 'http://' + request.META['HTTP_HOST'] + '/media/%s_1.docx' % (m1.number)
        else:
            resp_dict['error'] = '1'
            resp_dict['text']  = _('Document form is impossible.')        

    elif doc_action == 'docx_without_group':
        file_full_name = os.path.join(settings.MEDIA_ROOT, m1.number + '_0.docx')
        # генерация печатной версии документа без группировки наименований
        document = Document()
        table = document.add_table(rows=1, cols=2)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = _('Number')
        hdr_cells[1].text = _('The name of the cartridge')
        for item in jsontext:
            row_cells = table.add_row().cells
            row_cells[0].text = str(item[0])
            row_cells[1].text = str(item[1])
        document.add_page_break()
        document.save(file_full_name)
        resp_dict['error'] = '0'
        resp_dict['text']  = _('Document %(doc_number)s_0.docx generated') % { 'doc_number': m1.number }
        resp_dict['url'] = 'http://' + request.META['HTTP_HOST'] + '/media/%s_0.docx' % (m1.number)
    else:
        resp_dict['error'] = '1'
        resp_dict['text']  = _('This action is not implemented.')
    
    return JsonResponse(resp_dict, safe=False)

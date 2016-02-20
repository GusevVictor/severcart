# -*- coding:utf-8 -*-

import os, io
import time
import json
from django.http import JsonResponse, HttpResponse
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext as _
from docx import Document
from docx.shared import Inches
from index.models import CartridgeItemName, CartridgeType, CartridgeItem
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


@check_ajax_auth
def generate_csv(request):
    import csv, glob
    resp_dict = {}
    csv_file_name = str(int(time.time())) + '_' + str(request.user.pk) + '.csv'
    view = request.POST.get('view', '')
    if not os.path.exists(settings.STATIC_ROOT_CSV):
        os.makedirs(settings.STATIC_ROOT_CSV)
    # Прозводим ротацию каталога csv от старых файлов
    files = filter(os.path.isfile, glob.glob(settings.STATIC_ROOT_CSV + '\*.csv'))
    files = list(files)
    files.sort(key=lambda x: os.path.getmtime(x))
    try:
        if len(files) > settings.MAX_COUNT_CSV_FILES:
            os.remove(files[0])
    except:
        pass
    csv_full_name = os.path.join(settings.STATIC_ROOT_CSV, csv_file_name)
    all_items = CartridgeItem.objects.all().order_by('pk')
    if view == 'stock':
        all_items = all_items.filter(cart_status=1).filter(departament=request.user.departament)
        with open(csv_full_name, 'w', newline='') as csvfile:
            fieldnames = ['number', 'name', 'refills', 'date', 'comment']
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
            writer.writerow({'number': _('Number'), 
                            'name': _('Name'), 
                            'refills': _('Amount<br/>recovery'), 
                            'date': _('Date add') + ' ' + _('on stock'), 
                            'comment': _('comment')})
            for cartridje in all_items:
                writer.writerow({'number': cartridje.cart_number, 
                                'name': cartridje.cart_itm_name, 
                                'refills': cartridje.cart_number_refills, 
                                'date': cartridje.cart_date_change, 
                                'comment': cartridje.comment})
    elif view == 'use':
        try:
            root_ou   = request.user.departament
            children  = root_ou.get_family()
        except AttributeError:
            children = ''
        all_items = all_items.filter(departament__in=children).filter(cart_status=2)
        with open(csv_full_name, 'w', newline='') as csvfile:
            fieldnames = ['number', 'name', 'refills', 'date', 'org', 'comment']
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
            writer.writerow({'number': _('Number'), 
                            'name': _('Name'), 
                            'refills': _('Amount<br/>recovery'), 
                            'date': _('Date transfe'),
                            'org': _('User'),
                            'comment': _('comment')})
            for cartridje in all_items:
                writer.writerow({'number': cartridje.cart_number, 
                                'name': cartridje.cart_itm_name, 
                                'refills': cartridje.cart_number_refills, 
                                'date': cartridje.cart_date_change,
                                'org': cartridje.departament,
                                'comment': cartridje.comment})
    elif view == 'empty':
        all_items = all_items.filter( Q(departament=request.user.departament) & Q(cart_status=3) )
        with open(csv_full_name, 'w', newline='') as csvfile:
            fieldnames = ['number', 'name', 'refills', 'date', 'comment']
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
            writer.writerow({'number': _('Number'), 
                            'name': _('Name'), 
                            'refills': _('Amount<br/>recovery'), 
                            'date': _('Date return'), 
                            'comment': _('comment')})
            for cartridje in all_items:
                writer.writerow({'number': cartridje.cart_number, 
                                'name': cartridje.cart_itm_name, 
                                'refills': cartridje.cart_number_refills, 
                                'date': cartridje.cart_date_change,
                                'comment': cartridje.comment})

    elif view == 'at_work':
        all_items = all_items.filter(Q(cart_status=4) & Q(departament=request.user.departament))
        with open(csv_full_name, 'w', newline='') as csvfile:
            fieldnames = ['number', 'name', 'refills', 'date', 'firm', 'comment']
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
            writer.writerow({'number': _('Number'), 
                            'name': _('Name'), 
                            'refills': _('Amount<br/>recovery'), 
                            'date': _('Date transfer on recovery'), 
                            'firm': _('Refueller'),
                            'comment': _('comment')})
            for cartridje in all_items:
                writer.writerow({'number': cartridje.cart_number, 
                                'name': cartridje.cart_itm_name, 
                                'refills': cartridje.cart_number_refills, 
                                'date': cartridje.cart_date_change,
                                'firm': cartridje.filled_firm,
                                'comment': cartridje.comment})
    elif view == 'basket':
        all_items = all_items.filter( (Q(cart_status=5) | Q(cart_status=6)) & Q(departament=request.user.departament) )
        with open(csv_full_name, 'w', newline='') as csvfile:
            fieldnames = ['number', 'name', 'refills', 'date', 'firm', 'comment']
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
            writer.writerow({'number': _('Number'), 
                            'name': _('Name'), 
                            'refills': _('Amount<br/>recovery'), 
                            'date': _('Date return in basket'), 
                            'comment': _('comment')})
            for cartridje in all_items:
                writer.writerow({'number': cartridje.cart_number, 
                                'name': cartridje.cart_itm_name, 
                                'refills': cartridje.cart_number_refills, 
                                'date': cartridje.cart_date_change,
                                'comment': cartridje.comment})
    else:
        return HttpResponse(resp_dict, status_code=501)
    
    resp_dict['url'] = request.META.get('HTTP_ORIGIN') + settings.STATIC_URL + 'csv/' + csv_file_name
    return JsonResponse(resp_dict)

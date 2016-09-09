# -*- coding:utf-8 -*-

from django.utils.translation import ugettext as _
from datetime import timedelta

def date_to_str(date_dict):
    """Преобразует словарь содержащий компоненты дат в строку.
    """
    if isinstance(date_dict, dict):
        day   = date_dict.get('date_value', '')
        month = date_dict.get('month_value', '')
        year  = date_dict.get('year_value', '')
    else:
        return ''
    # добавляем лидирующий ноль
    day   = '0' + str(day) if day < 10 else str(day)
    month = '0' + str(month) if month < 10 else str(month)
    year  = str(year)

    if _('lang') == 'ru':
        return '/'.join([ day, month, year ])
    else:
        return '/'.join([ month, day, year ])


def events_decoder(qso, time_zone_offset, simple=True):
    """Функция докодер симолических мнемоник в человекочитаемый формат. 
        Единственный обязательный аргумент на входе - список объектов QuerySet
    """
    frdly_es = []

    for entry in qso:
        if entry.event_type == 'AD':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = _('Added user %(user_name)s.') % {'user_name': entry.event_user}
            else:
                text_com = _('№ %(cart_number)s (%(cart_type)s) added user %(user_name)s.') % {'cart_number': entry.cart_number, 
                                                                                                'cart_type': entry.cart_type, 
                                                                                                'user_name': entry.event_user}
            entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'ADE':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = _('Added empty cartridge user %(user_name)s.') % {'user_name': entry.event_user}
            else:
                text_com = _('Added empty cartridge № %(cart_number)s (%(cart_type)s) user %(user_name)s.') % {'cart_number': entry.cart_number, 
                                                                                                'cart_type': entry.cart_type, 
                                                                                                'user_name': entry.event_user}
            entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TR':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = _('Transfer to use %(event_org)s user %(event_user)s.') % {'event_org': entry.event_org, 'event_user': entry.event_user }
            else:
                text_com = _('№ %(cart_number)s (%(cart_type)s) transfer to use %(event_org)s user %(event_user)s.') % { 'cart_number': entry.cart_number, 
                                                                                    'cart_type': entry.cart_type, 
                                                                                    'event_org': entry.event_org,
                                                                                    'event_user': entry.event_user }
            entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TF':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = _('Transfer to restore "%(event_firm)s" user %(event_user)s.') % {'event_firm': entry.event_firm,
                                                                            'event_user': entry.event_user }
            else:
                text_com = _('№ %(cart_number)s (%(cart_type)s) transfer to restore "%(event_firm)s" user %(event_user)s.') % {
                                                                            'cart_number': entry.cart_number, 
                                                                            'cart_type': entry.cart_type, 
                                                                            'event_firm': entry.event_firm,
                                                                            'event_user': entry.event_user }
            entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'RS':
            entry_obj   = {}
            data_env    = entry.date_time
            entry.cart_action = '00000' if entry.cart_action == 0 else entry.cart_action
            action_num  = [ int(i) for i in str(entry.cart_action) ]
            action_text = ''
            action_text += _('filling and cleaning, ') if action_num[0] == 1 else ''
            action_text += _('Replacement fotoreceptor, ') if action_num[1] == 1 else ''
            action_text += _('replacement of squeegee, ') if action_num[2] == 1 else ''
            action_text += _('chip replacement, ') if action_num[3] == 1 else ''
            action_text += _('replacing the magnetic roller, ') if action_num[4] == 1 else ''
            if simple:
                text_com = _('Return to the filling in the firm "%(event_firm)s" user %(event_user)s.') % {
                                                                        'event_firm': entry.event_firm,
                                                                        'event_user': entry.event_user }
            else:
                text_com = _('№ %(cart_number)s (%(cart_type)s) return to the filling in the firm "%(event_firm)s" user %(event_user)s.') % {
                                                                        'cart_number': entry.cart_number, 
                                                                        'cart_type': entry.cart_type, 
                                                                        'event_firm': entry.event_firm,
                                                                        'event_user': entry.event_user }
            text_com += _('<br/>The following work: ')
            text_com += action_text 
            entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TB':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = _('Moving in user to basket %(event_user)s.') % {'event_user': entry.event_user, }
            else:
                text_com = _('№ %(cart_number)s (%(cart_type)s) moving in user to basket %(event_user)s.') % {
                                                                                'cart_number': entry.cart_number, 
                                                                                'cart_type': entry.cart_type, 
                                                                                'event_user': entry.event_user, }
            entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'DC':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = _('Deleted user %(event_user)s.') % {'event_user': entry.event_user}
            else:
                text_com = _('№ %(cart_number)s (%(cart_type)s) deleted user %(event_user)s.') % { 
                                                                    'cart_number': entry.cart_number, 
                                                                    'cart_type': entry.cart_type, 
                                                                    'event_user': entry.event_user, }
            entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TS':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = _('Return to stock from %(event_org)s user %(event_user)s.') % {'event_org': entry.event_org,
                                                                                       'event_user': entry.event_user, }
            else:
                text_com = _('№ %(cart_number)s (%(cart_type)s) return to stock from %(event_org)s user %(event_user)s.') % {
                                                                        'cart_number': entry.cart_number, 
                                                                        'cart_type': entry.cart_type, 
                                                                        'event_org': entry.event_org,
                                                                        'event_user': entry.event_user }
            entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

    return frdly_es
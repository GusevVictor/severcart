# -*- coding:utf-8 -*-

from datetime import datetime, tzinfo
from django.utils.translation import ugettext as _
import pytz
from django.utils import timezone, six
from service.helpers import SevercartConfigs


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


# HACK: datetime is an old-style class, create a new-style equivalent
# so we can define additional attributes.
class datetimeobject(datetime, object):
    pass


def do_timezone(value, arg):
    """
    Конвертрирует объект value класса datetime в локальное время, заданной временной зоны.
    Converts a datetime to local time in a given time zone.


    Второй аргумент является строкой формата 'Asia/Yekaterinburg'
    """

    arg = pytz.timezone(arg)
    #if not isinstance(value, type(datetime)):
    #    print('isinstance!')
    #    return ''

    # Obtain a timezone-aware datetime
    try:
        if timezone.is_naive(value):
            default_timezone = timezone.get_default_timezone()
            value = timezone.make_aware(value, default_timezone)
    # Filters must never raise exceptions, and pytz' exceptions inherit
    # Exception directly, not a specific subclass. So catch everything.
    except Exception:
        return ''

    # Obtain a tzinfo instance
    if isinstance(arg, tzinfo):
        tz = arg
    elif isinstance(arg, six.string_types) and pytz is not None:
        try:
            tz = pytz.timezone(arg)
        except pytz.UnknownTimeZoneError:
            return ''
    else:
        return ''

    result = timezone.localtime(value, tz)

    # HACK: the convert_to_local_time flag will prevent
    #       automatic conversion of the value to local time.
    result = datetimeobject(result.year, result.month, result.day,
                            result.hour, result.minute, result.second,
                            result.microsecond, result.tzinfo)
    result.convert_to_local_time = False
    return result


def events_decoder(qso, time_zone_offset, simple=True):
    """Функция докодер симолических мнемоник в человекочитаемый формат. 
        Единственный обязательный аргумент на входе - список объектов QuerySet
    """
    frdly_es = []
    conf = SevercartConfigs()
    current_tz = pytz.timezone(conf.time_zone)
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
            #entry_obj['data_env'] = data_env + timedelta(hours=time_zone_offset)
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
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
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
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
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
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
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'RS':
            entry_obj   = {}
            data_env    = entry.date_time
            action_text = ''
            if len(str(entry.cart_action)) == 5:
                # поддержка старых релизов severcart
                entry.cart_action = '00000' if entry.cart_action == 0 else entry.cart_action
                action_num  = [ int(i) for i in str(entry.cart_action) ]
                action_text += _('filling and cleaning, ') if action_num[0] == 1 else ''
                action_text += _('Replacement fotoreceptor, ') if action_num[1] == 1 else ''
                action_text += _('replacement of squeegee, ') if action_num[2] == 1 else ''
                action_text += _('chip replacement, ') if action_num[3] == 1 else ''
                action_text += _('replacing the magnetic roller, ') if action_num[4] == 1 else ''
                
            elif len(str(entry.cart_action)) == 6:
                entry.cart_action = '000000' if entry.cart_action == 0 else entry.cart_action
                action_num  = [ int(i) for i in str(entry.cart_action) ]
                action_text += _('regeneration, ') if action_num[0] == 1 else ''
                action_text += _('filling and cleaning, ') if action_num[1] == 1 else ''
                action_text += _('Replacement fotoreceptor, ') if action_num[2] == 1 else ''
                action_text += _('replacement of squeegee, ') if action_num[3] == 1 else ''
                action_text += _('chip replacement, ') if action_num[4] == 1 else ''
                action_text += _('replacing the magnetic roller, ') if action_num[5] == 1 else ''
            else:
                action_text = _('Not implement.')
                
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
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
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
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
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
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
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
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)
        elif entry.event_type == 'CN':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = _('%(event_user)s produced has replaced the former number %(old_number)s new %(new_number)s.') % {'old_number': entry.cart_old_number,
                                                                                           'new_number': entry.cart_number,
                                                                                       'event_user': entry.event_user, 
                                                                                       }
            else:
                text_com = _('%(event_user)s changed number of cartridge %(old_number)s new %(new_number)s.') % {'old_number': entry.cart_old_number,
                                                                                           'new_number': entry.cart_number,
                                                                                       'event_user': entry.event_user, 
                                                                                       }
            entry_obj['data_env'] = do_timezone(data_env, conf.time_zone)
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

    return frdly_es

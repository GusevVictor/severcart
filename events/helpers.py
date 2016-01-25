# -*- coding:utf-8 -*-

def events_decoder(qso, simple=True):
    """Функция докодер симолических мнемоник в человекочитаемый формат. 
        Единственный обязательный аргумент на входе - объект QuerySet
    """
    frdly_es = []
    for entry in qso:
        if entry.event_type == 'AD':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = 'Добавлен пользователем %s.' % (entry.event_user, )
            else:
                text_com = '№ %s (%s) добавлен пользователем %s.' % (entry.cart_number, entry.cart_type, entry.event_user)
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TR':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = 'Передача в пользование %s пользователем %s.' % (
                                                                            entry.event_org,
                                                                            entry.event_user )
            else:
                text_com = '№ %s (%s) передан в пользование %s пользователем %s.' % (entry.cart_number, 
                                                                                    entry.cart_type, 
                                                                                    entry.event_org,
                                                                                    entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TF':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = 'Передача на заправку "%s" пользователем %s.' % (
                                                                            entry.event_firm,
                                                                            entry.event_user )
            else:
                text_com = '№ %s (%s) передача на заправку "%s" пользователем %s.' % (entry.cart_number, 
                                                                            entry.cart_type, 
                                                                            entry.event_firm,
                                                                            entry.event_user )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'RS':
            entry_obj   = {}
            data_env    = entry.date_time
            entry.cart_action = '00000' if entry.cart_action == 0 else entry.cart_action
            action_num  = [ int(i) for i in str(entry.cart_action) ]
            action_text = ''
            action_text += 'заправка и очистка, ' if action_num[0] == 1 else ''
            action_text += 'замена фотовала, ' if action_num[1] == 1 else ''
            action_text += 'замена ракеля, ' if action_num[2] == 1 else ''
            action_text += 'замена чипа, ' if action_num[3] == 1 else ''
            action_text += 'замена магнитного вала, ' if action_num[4] == 1 else ''
            if simple:
                text_com = 'Возврат с заправки в фирме "%s" пользователем %s.' % (
                                                                        entry.event_firm,
                                                                        entry.event_user )
            else:
                text_com = '№ %s (%s) возвращён с заправки в фирме "%s" пользователем %s.' % (
                                                                        entry.cart_number, 
                                                                        entry.cart_type, 
                                                                        entry.event_firm,
                                                                        entry.event_user )
            text_com += '<br/>Проводились следующие работы: '
            text_com += action_text 
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TB':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = 'Перемещение в корзину пользователем %s.' % (entry.event_user, )
            else:
                text_com = '№ %s (%s) перемещён в корзину пользователем %s.' % (entry.cart_number, entry.cart_type, entry.event_user, )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'DC':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = 'Списание пользователем %s.' % (entry.event_user, )
            else:
                text_com = '№ %s (%s) списан пользователем %s.' % (entry.cart_number, entry.cart_type, entry.event_user, )
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

        elif entry.event_type == 'TS':
            entry_obj = {}
            data_env = entry.date_time
            if simple:
                text_com = 'Возврат на склад от %s пользователем %s.' % (entry.event_org,
                                                                        entry.event_user)
            else:
                text_com = '№ %s (%s) возвращён на склад от %s пользователем %s.' % (
                                                                        entry.cart_number, 
                                                                        entry.cart_type, 
                                                                        entry.event_org,
                                                                        entry.event_user)
            entry_obj['data_env'] = data_env
            entry_obj['text_com'] = text_com
            frdly_es.append(entry_obj)

    return frdly_es
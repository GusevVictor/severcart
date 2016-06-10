# -*- coding:utf-8 -*-

import operator
import logging
from events.helpers import date_to_str
from django.conf import settings

def group_names(any_list=None):
    """Принимает список наменований и номеров в формате [[1, 'CE505A'], [2, 'CE505A'], [3, 'CE505A'], [6, 'Q7553A'], [7, 'Q7553A'], ]
        Каждый элемент списка, пара с списком, первый элемент - номер расходного материала, второй - название картриджа.

        Возвращает словарь содержащий результат группировки в виде {'CE505A': 3, 'Q7553A': 2}
        Ключ содержит имя, значение - количество повторений.
    """
    logger = logging.getLogger('simp')
    
    if not any_list:
        return None
    if not isinstance(any_list, list):
        return None
    result = dict()
    try:
        for elem in any_list:
            if result.get(elem[1], ''):
                result[elem[1]] = result.get(elem[1]) + 1
            else:
                result[elem[1]] = 1
    except:
        logger.error('Input object not correct JSON desirialize object!')
        return None
    # генерируем список, отсортированный по возврастанию количества
    result = sorted(result.items(), key=operator.itemgetter(1))
    return result

def localize_date(date_obj):
    """
    """
    date_obj = date_to_str({'date_value': date_obj.day, 
                            'month_value': date_obj.month, 
                            'year_value': date_obj.year})
    
    return date_obj

if __name__ == '__main__':
    """Simple unit test ;)
    """
    #jo = [[1, 'CE505A'], [2, 'CE505A'], [3, 'CE505A'], [6, 'Q7553A'], [7, 'Q7553A'], ]
    jo = [[1, 'CE505A'], [2, 'CE505A'], [3, 'CE505A'], [6, 'Q7553A'], [7, 'Q7553A'], [5, 'Q7549A'],]
    #jo = [[1, 'CE505A'], [2, 'CE505A'], [3, 'CE505A'], [6, 'Q7553A'], ['Q7553A'], ]
    #jo = 123
    #jo = []
    print(group_names(jo))

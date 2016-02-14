# -*- coding:utf-8 -*-

from django.conf import settings

class ShortList(object):
    """Специфический список, циклически удаляющий первые элементы
       при переполнении. Настраивается через settings django.
       При возврате обратно удаляет последний элемент.
    """
    def __init__(self, prepare_list):
        self.prepare_list = prepare_list

    def push(self, elem):
        # если пользователь движетестся по ссылкам вверх, то добавляем юрл в список
        if self.prepare_list.count(elem) == 0:
            self.prepare_list.append(elem)
        else:
            # если пользователь движется обратно, то выталкиваем последний элемент
            self.prepare_list.pop(-1)
        
        # чтобы исключить чрезмерное расходавание памяти, окраничим список фиксированным значением
        if len(self.prepare_list) > settings.HISTORY_LENGTH:
            self.prepare_list.pop(0) # убираем первый элемент, 2 элемент становится на место первого

    def get(self, index):
        return self.prepare_list[index]

    def dump(self):
        return self.prepare_list        


class BreadcrumbsPath(object):
    """Класс реализует работу кнопки возврата обратно.
       Получает на вход объект request, извлекает из него сессию текущего юзера.
       Далее перезаписывает сессионную переменную новым значением. 
    """    
    def __init__(self, request=None):
        if request.session.get('bcback', False):
            # загружаем список из сессии
            bread_list = ShortList(request.session['bcback'])
            end_elem = bread_list.get(-1)
            if request.META['PATH_INFO'] != end_elem:
                # если пользователь поменял страницу
                bread_list.push(request.META['PATH_INFO'])
                request.session['bcback'] = bread_list.dump()
            else:
                pass

        else:
            # инициализация при первом заходе после установки
            bread_list = []
            bread_list.append(request.META['PATH_INFO'])
            request.session['bcback'] = bread_list

        # возвращаем не инстанс класса, а строку с данными

    @staticmethod
    def before_page(request=None):
        """Возвращает предыдущую страницу
        """
        bread_list = request.session['bcback']
        current_url = request.META['PATH_INFO']
        index_current_url = bread_list.index(current_url, -1)
        if len(bread_list) >= 2:
            return bread_list[index_current_url-1]
        else:
            return None


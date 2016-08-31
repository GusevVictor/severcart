# -*- coding:utf-8 -*-

from django.conf import settings
from django.shortcuts import render
from reportlab.graphics.barcode import code128, code39, qr
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm


def del_leding_zero(data):
    """Убираем лидирующий ноль, если он есть.
    """
    if data[0] == '0':
        return int(data[1:])
    else:
        return int(data)

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
            if request.path_info != end_elem:
                # если пользователь поменял страницу
                bread_list.push(request.path_info)
                request.session['bcback'] = bread_list.dump()
            else:
                pass

        else:
            # инициализация при первом заходе после установки
            bread_list = []
            bread_list.append(request.path_info)
            request.session['bcback'] = bread_list

        # возвращаем не инстанс класса, а строку с данными

    @staticmethod
    def before_page(request=None):
        """Возвращает предыдущую страницу
        """
        bread_list = request.session['bcback']
        current_url = request.path_info
        index_current_url = bread_list.index(current_url)
        if len(bread_list) >= 2:
            return bread_list[index_current_url-1]
        else:
            return None

def is_admin(view_method):
    "Проверяем, является ли пользователь администратором."
    def wrapper(request, *args, **kwargs):
        if request.user.is_admin:
            return view_method(request, *args, **kwargs)
        else:
            return render(request, 'accounts/is_not_admin.html', context={})
        
    return wrapper


class Sticker(object):
    """Ресует наклейки на странице А4.
    """
    
    def __init__(self, file_name='hello3.pdf', pagesize='A4', print_bar_code=False):
        """
        """
        self.count  = 0
        self.page   = 1
        self.row    = 0
        self.column = 0
        self.pagesize = pagesize
        self.print_bar_code = print_bar_code
        if pagesize == 'A4':
            pagesize = A4
        elif pagesize == 'A5':
            pagesize = A5
        else:
            pagesize = A4

        self.canv   = canvas.Canvas(file_name, pagesize=pagesize)
        self.canv.translate(mm, mm)
        self.font_size = 2.5*mm # максмальное количество символов в ячейке - 14
        self.canv.setFont('Courier-Bold', self.font_size)

    def add(self, ou_number='5', cartridge_name='Q2612A', cartridge_number='1245'):
        """Рисует одну наклейку. 
        """
        if self.print_bar_code:
            if self.pagesize == 'A4':
                x = 10 + (self.column * 19.5)
                y = 275 - (self.row * 22.0)
            elif self.pagesize == 'A5':
                x = 7 + (self.column * 19.5)
                y = 185 - (self.row * 24)
            else:
                x = 10 + (self.column * 19.5)
                y = 283 - (self.row * 14.7)

            #cartridge_number = "99999" максимально вмещаемый номер
            # рисуем штрихкод и рамочку к нему
            #self.canv.rect(x*mm, y*mm, 16.5*mm, 7.5*mm, fill=0)

            #barcode128 = code128.Code128(cartridge_number, barHeight= 1*mm, barWidth = 1*mm)
            #barcode128.drawOn(self.canv, (x-5.5)*mm, (y+0.6)*mm)
            from reportlab.graphics.shapes import Drawing 
            from reportlab.graphics import renderPDF
            # draw a QR code
            qr_code = qr.QrCodeWidget(str(cartridge_number))
            bounds = qr_code.getBounds()
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            d = Drawing(10, 10, transform=[45./width,0,0,45./height,0,0])
            d.add(qr_code)
            renderPDF.draw(d, self.canv, (x+0.9)*mm, (y-1.6)*mm)

            # отрисовываем прямоугольник с номером организации
            #self.canv.rect(x*mm, y*mm, 16.5*mm, 4*mm, fill=0)
            #self.canv.drawString(x*mm, (y+1)*mm, self.center(ou_number))
            self.canv.rect((x-0)*mm, (y-4)*mm, 16.5*mm, 4*mm, fill=0)
            self.canv.drawString((x-0)*mm, (y-3)*mm, self.center(str(cartridge_name)))

            self.canv.rect((x-0)*mm, (y-8)*mm, 16.5*mm, 4*mm, fill=0)
            self.canv.drawString((x-0)*mm, (y-7)*mm, self.center(cartridge_number))
        else:
            # печатаем наклейку если не выбрана опция "Печатать штрихкод"
            if self.pagesize == 'A4':
                x = 10 + (self.column * 19.5)
                y = 283 - (self.row * 14.7)
            elif self.pagesize == 'A5':
                x = 7 + (self.column * 19.5)
                y = 198 - (self.row * 14)
            else:
                x = 10 + (self.column * 19.5)
                y = 283 - (self.row * 14.7)

            self.canv.rect(x*mm, y*mm, 16.5*mm, 4*mm, fill=0)
            self.canv.drawString(x*mm, (y+1)*mm, self.center(ou_number))

            self.canv.rect((x-0)*mm, (y-4)*mm, 16.5*mm, 4*mm, fill=0)
            self.canv.drawString((x-0)*mm, (y-3)*mm, self.center(cartridge_name))

            self.canv.rect((x-0)*mm, (y-8)*mm, 16.5*mm, 4*mm, fill=0)
            self.canv.drawString((x-0)*mm, (y-7)*mm, self.center(cartridge_number))
        self.column += 1
        # Если количество наклеек превышает 10, то обнуляем счётчик колонок и
        # инкрементируем счётчик строк.
        if self.pagesize == 'A4': 
            MAX_COLUMNS = 10
            MAX_ROWS    = 19
        elif self.pagesize == 'A5':
            MAX_COLUMNS = 7
            MAX_ROWS    = 13
        else:
            # A4 по-умолчанию
            MAX_COLUMNS = 10
            MAX_ROWS    = 19

        if self.column == MAX_COLUMNS:
            self.column = 0
            self.row += 1

        if self.row == MAX_ROWS:
            self.row = 0
            # добавляем новыую пустую страницу.
            self.page_break()
        self.count  += 1

    def center(self, str_obj):
        """Центрирует строку по ширине наклейки добавляя слева пробельные символы.
        """
        import math
        str_obj = str(str_obj)
        if len(str_obj) == 11:
            left_padding = 0
        elif len(str_obj) > 11:
            #усекаем строку слева, результирующая строка = 11 символам 
            str_obj = str_obj[-11:]
            left_padding = 0
        else:
            left_padding = math.ceil((11 - len(str_obj)) / 2)
        return ' '*left_padding + str_obj


    def page_break(self):
        """
        """
        self.canv.showPage()
        self.canv.setFont('Courier-Bold', self.font_size)

    def fin(self):
        """Формируем результирующий документ.
        """
        self.canv.showPage()
        self.canv.save()


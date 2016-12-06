# -*- coding:utf-8 -*-

def pretty_list(mystr):
    """Улучшаем визуальное представление списка израсходованных РМ
    """
    mystr = str(mystr)
    mystr = mystr.replace('[', '')
    mystr = mystr.replace(']', '')
    mystr = mystr.replace('{', '')
    mystr = mystr.replace('}', '')
    mystr = mystr.replace('cart_type', '')
    mystr = mystr.replace('\'', '')
    mystr = mystr.replace(': ', '')
    return mystr
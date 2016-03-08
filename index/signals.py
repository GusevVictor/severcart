# -*- coding:utf-8 -*-

from django.apps import AppConfig
from django.dispatch import Signal
from django.utils import timezone
from .models import CartridgeItem
from events.models import Events
from django.db import transaction


sign_add_full_to_stock       = Signal(providing_args=['num', 'cart_type', 'user', 'request'])
sign_add_empty_to_stock      = Signal(providing_args=['num', 'cart_type', 'user', 'request'])
sign_tr_cart_to_uses         = Signal(providing_args=['list_cplx', 'org' , 'request'])
sign_tr_cart_to_basket       = Signal(providing_args=['list_cplx', 'request'])
sign_tr_empty_cart_to_stock  = Signal(providing_args=['list_cplx', 'request'])
sign_turf_cart               = Signal(providing_args=['list_cplx', 'request'])
sign_tr_empty_cart_to_firm   = Signal(providing_args=['list_cplx', 'request','firm'])
sign_tr_filled_cart_to_stock = Signal(providing_args=['list_cplx', 'request'])

def event_add_cart(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Error in handler event_add_cart!')
    
    with transaction.atomic():
        for elem in kwargs.get('list_cplx'):
            m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_index  = elem[0],
                cart_number = elem[1],
                cart_type   = elem[2],
                event_type  = 'AD',
                event_user  = str(kwargs.get('request').user),
            )
            m1.save()

def event_add_empty_cart(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Error in handler event_add_cart!')
    
    with transaction.atomic():
        for elem in kwargs.get('list_cplx'):
            m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_index  = elem[0],
                cart_number = elem[1],
                cart_type   = elem[2],
                event_type  = 'ADE',
                event_user  = str(kwargs.get('request').user),
            )
            m1.save()


def event_transfe_cart_to_uses(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Error in handler event_transfe_cart_to_uses!')
    
    with transaction.atomic():
        for elem in kwargs.get('list_cplx'):
            m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_index = elem[0],
                cart_type   = elem[1],
                cart_number = elem[2],
                event_type  = 'TR',
                event_user  = str(kwargs.get('request').user),
                event_org   = kwargs.get('org')
            )
            m1.save()

def event_transfe_cart_to_basket(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Error in handler event_transfe_cart_to_basket!')
    
    with transaction.atomic():
        for elem in kwargs.get('list_cplx'):
            m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_index  = elem[0],
                cart_type   = elem[1],
                cart_number = elem[2],
                event_type  = 'TB',
                event_user  = str(kwargs.get('request').user),
            )
            m1.save()


def event_tr_empty_cart_to_stock(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Error in handler event_tr_empty_cart_to_stock!')

    with transaction.atomic():
        for elem in kwargs.get('list_cplx'):
            m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_index = elem[0],
                cart_type   = elem[1],
                event_type  = 'TS',
                event_user  = str(kwargs.get('request').user),
                event_org   = elem[2],
                cart_number = elem[3],
            )
            m1.save()


def event_turf_cart(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Error in handler event_turf_cart!')

    with transaction.atomic():
        for elem in kwargs.get('list_cplx'):
            m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_index  = elem[0],
                cart_type   = elem[1],
                cart_number = elem[2],
                event_type  = 'DC',
                event_user  = str(kwargs.get('request').user),
            )
            m1.save()

def event_tr_empty_cart_to_firm(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Error in handler event_tr_empty_cart_to_firm!')

    with transaction.atomic():
        for elem in kwargs.get('list_cplx'):
            m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_index  = elem[0],
                cart_type   = elem[1],
                cart_number = elem[2],
                event_type  = 'TF',
                event_firm  = kwargs.get('firm'),
                event_user  = str(kwargs.get('request').user),
            )
            m1.save()


def event_tr_filled_cart_to_stock(**kwargs):
    if len(kwargs.get('list_cplx', 0)) == 0:
        raise ValueError('Error in handler event_tr_filled_cart_to_stock!')

    with transaction.atomic():    
        for elem in kwargs.get('list_cplx'):
            actions = elem[3]
            compact_num = 0
            for act in actions:
                if act == 'filled':
                    compact_num += 10000
                elif act == 'fotoreceptor':
                    compact_num += 1000
                elif act == 'rakel':
                    compact_num += 100
                elif act == 'chip':
                    compact_num += 10
                elif act == 'magnit':
                    compact_num += 1
                else:
                    compact_num += 0
            m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_index = elem[0],
                cart_type   = elem[1],
                event_type  = 'RS',
                event_firm  = elem[2],
                event_user  = str(kwargs.get('request').user),
                cart_action = compact_num,
                cart_number = elem[4],
            )
            m1.save()

sign_add_full_to_stock.connect(event_add_cart)
sign_add_empty_to_stock.connect(event_add_empty_cart)
sign_tr_cart_to_uses.connect(event_transfe_cart_to_uses)
sign_tr_cart_to_basket.connect(event_transfe_cart_to_basket)
sign_tr_empty_cart_to_stock.connect(event_tr_empty_cart_to_stock)
sign_turf_cart.connect(event_turf_cart)
sign_tr_empty_cart_to_firm.connect(event_tr_empty_cart_to_firm)
sign_tr_filled_cart_to_stock.connect(event_tr_filled_cart_to_stock)

# -*- config:utf-8 -*-
from django.dispatch import Signal
from django.utils import timezone
from .models import CartridgeItem
from events.models import Events

sign_add_full_to_stock       = Signal(providing_args=['num', 'cart_type', 'user', 'request'])
sign_tr_cart_to_uses         = Signal(providing_args=['num', 'cart_type', 'counts', 'org' , 'user'])
sign_tr_empty_cart_to_stock  = Signal(providing_args=['num', 'cart_type', 'counts', 'user'])
sign_tr_cart_to_basket       = Signal(providing_args=['num_type_counts_dict', 'user'])
sign_turf_cart               = Signal(providing_args=['num_type_counts_dict', 'user'])
sign_tr_empty_cart_to_firm   = Signal(providing_args=['num_type_counts_dict','firm', 'user'])
sign_tr_filled_cart_to_stock = Signal(providing_args=['num_type_counts_dict','firm', 'user'])

#@receiver(add_full_to_stock, sender=CartridgeItem, dispatch_uid='generate_event')
def event_add_cart(**kwargs):
    """departament,  date_time, cart_number,  cart_type, 
        event_type, event_user, event_org, event_firm
    """
    m1 = Events(departament = kwargs.get('request').user.departament.pk,
                date_time   = timezone.now(),
                cart_number = kwargs.get('num', 0),
                cart_type   = kwargs.get('cart_type', 0),
                event_type  = 'AD',
                event_user  = kwargs.get('user', 'anonymous'),
                )
    m1.save()    
    #print('signal kwargs', kwargs)


"""
signal kwargs {'num': 276, 'sender': None, 
'user': 'root', 'request': <WSGIRequest: POST '/add_items/'>, 
'signal': <django.dispatch.dispatcher.Signal object at 0x02B1B510>, 
'cart_type': 'CE505A'}
"""

sign_add_full_to_stock.connect(event_add_cart)

# class CartridgeStore(object):
#     """Служебный класс для отправки сигналов.
#     """

#     def __init__(self):
#         pass


#     def add_full_to_stock(self, num, cart_type, counts, user):
#         """Добавление N количества новых картриджей на склад.
#         """
#         add_full_to_stock.send(sender=self.__class__, 
#                                 num=num, 
#                                 cart_type=cart_type, 
#                                 counts=counts, 
#                                 user=user)


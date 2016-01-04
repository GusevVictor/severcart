from django.conf.urls import url
from index.views import dashboard
from index.views import stock
from index.views import add_cartridge_name
from index.views import add_cartridge_item
from index.views import tree_list
from index.views import add_type
from index.views import transfe_for_use
from index.views import transfer_to_stock
from index.views import transfer_to_firm
from index.views import from_firm_to_stock
from index.views import transfe_to_basket
from index.views import from_basket_to_stock
from index.views import at_work
from index.views import use
from index.views import empty
from index.views import toner_refill
from index.views import add_city
from index.views import add_firm
from index.views import edit_firm
from index.views import del_firm
from index.views import at_work
from index.views import bad_browser
from index.views import basket

urlpatterns = [
    url('^$', dashboard, name='dashboard'),
    url('^stock/', stock, name='stock'),
    url(r'^add_name/', add_cartridge_name, name='add_name'),
    url(r'^add_items/', add_cartridge_item, name='add_items'),
    url(r'^tree_list/', tree_list, name='tree_list'),
    url(r'^add_type/', add_type, name='add_type'),
    url(r'^transfe_for_use/', transfe_for_use, name='transfe_for_use'),
    url(r'^transfer_to_stock/', transfer_to_stock, name='transfer_to_stock'),
    url(r'^transfer_to_firm/', transfer_to_firm, name='transfer_to_firm'),
    url(r'^from_firm_to_stock/', from_firm_to_stock, name='from_firm_to_stock'),
    url(r'^transfe_to_basket/', transfe_to_basket, name='transfe_to_basket'),
    url(r'^from_basket_to_stock/', from_basket_to_stock, name='from_basket_to_stock'),
    url(r'^at_work/', at_work, name='at_work'),
    url(r'^use/', use, name='use'),
    url(r'^empty/', empty, name='empty'),
    url(r'^toner_refill/', toner_refill, name='toner_refill'),
    url(r'^add_city/', add_city, name='add_city'),
    url(r'^add_firm/', add_firm, name='add_firm'),
    url(r'^edit_firm/', edit_firm, name='edit_firm'),
    url(r'^del_firm/', del_firm, name='del_firm'),
    url(r'^at_work/', at_work, name='at_work'),
    url(r'^bad_browser/', bad_browser, name='bad_browser'),
    url(r'^basket/', basket, name='basket'),
]

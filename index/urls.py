from django.conf.urls import url

urlpatterns = [
    url('^$', 'index.views.index', name='stock'),
    url(r'^add_name/', 'index.views.add_cartridge_name', name='add_name'),
    url(r'^add_items/', 'index.views.add_cartridge_item', name='add_items'),
    url(r'^tree_list/', 'index.views.tree_list', name='tree_list'),
    url(r'^add_type/', 'index.views.add_type', name='add_type'),
    url(r'^transfe_for_use/', 'index.views.transfe_for_use', name='transfe_for_use'),
    url(r'^transfer_to_stock/', 'index.views.transfer_to_stock', name='transfer_to_stock'),
    url(r'^at_work/', 'index.views.at_work', name='at_work'),
    url(r'^use/', 'index.views.use', name='use'),
    url(r'^empty/', 'index.views.empty', name='empty'),
    url(r'^toner_refill/', 'index.views.toner_refill', name='toner_refill'),
    url(r'^add_city/', 'index.views.add_city', name='add_city'),
    url(r'^add_firm/', 'index.views.add_firm', name='add_firm'),
    url(r'^edit_firm/', 'index.views.edit_firm', name='edit_firm'),
    url(r'^del_firm/', 'index.views.del_firm', name='del_firm'),
]

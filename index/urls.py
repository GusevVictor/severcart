from django.conf.urls import url

urlpatterns = [
    url('^$', 'index.views.index'),
    url(r'^add_name/', 'index.views.add_cartridge_name'),
    url(r'^add_items/', 'index.views.add_cartridge_item'),
    url(r'^tree_list/', 'index.views.tree_list'),
    url(r'^add_type/', 'index.views.add_type'),
    url(r'^transfe_for_use/', 'index.views.transfe_for_use'),
    url(r'^transfer_to_stock/', 'index.views.transfer_to_stock'),
    url(r'^use/', 'index.views.use'),
    url(r'^empty/', 'index.views.empty'),
    url(r'^toner_refill/', 'index.views.toner_refill'),

]

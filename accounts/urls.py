from django.conf.urls import url
# urlpatterns = patterns(
#     url(r'register$', 'accounts.views.register', name='register'),
#     url(r'login$', 'accounts.views.login', name='login'),
#     url(r'logout$', 'accounts.views.logout', name='logout'),
# )

urlpatterns = [
    url(r'^$', 'index.views.manage_users', name='manage_users'),
    url(r'^add_user/', 'accounts.views.register', name='register'),
    url(r'^login/', 'accounts.views.login', name='login'),
    url(r'^logout/', 'accounts.views.logout', name='logout'),
    url(r'^edit/', 'accounts.views.edit', name='edit'),
    url(r'^delete/', 'accounts.views.delete', name='del'),
]

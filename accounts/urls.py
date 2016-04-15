from django.conf.urls import include, url
from .views import manage_users
from .views import ( register,
                   edit_user,
                   login,
                   logout,
                   edit,
                   delete,
                   change_password, 
                   send_email,
                   recover_password )

urlpatterns = [
    url(r'^$', manage_users, name='manage_users'),
    url(r'^add_user/', register, name='register'),
    url(r'^change_password/', change_password, name='change_password'),
    url(r'^edit_user/', edit_user, name='edit_user'),
    url(r'^login/', login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^edit/', edit, name='edit'),
    url(r'^delete/', delete, name='del'),
    url(r'^send_email/', send_email, name='send_email'),
    url(r'^recover_password/(?P<secret_key>[a-zA-Z0-9]{64})/$', recover_password, name='recover_password'),
    url(r'^api/', include('accounts.api.urls')),
]

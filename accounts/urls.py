from django.conf.urls import url
from .views import manage_users
from .views import ( register,
                   edit_user,
                   login,
                   logout,
                   edit,
                   delete,
                   change_password, )

urlpatterns = [
    url(r'^$', manage_users, name='manage_users'),
    url(r'^add_user/', register, name='register'),
    url(r'^change_password/', change_password, name='change_password'),
    url(r'^edit_user/', edit_user, name='edit_user'),
    url(r'^login/', login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^edit/', edit, name='edit'),
    url(r'^delete/', delete, name='del'),
]

from django.conf.urls import url
from index.views import manage_users
from accounts.views import register
from accounts.views import edit_user
from accounts.views import login
from accounts.views import logout
from accounts.views import edit
from accounts.views import delete

urlpatterns = [
    url(r'^$', manage_users, name='manage_users'),
    url(r'^add_user/', register, name='register'),
    url(r'^edit_user/', edit_user, name='edit_user'),
    url(r'^login/', login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^edit/', edit, name='edit'),
    url(r'^delete/', delete, name='del'),
]

from django.conf.urls import url, include
from .views import main_summary, amortizing, users

urlpatterns = [
    url(r'^$', main_summary, name='main_summary'),
    url(r'^amortizing/', amortizing, name='amortizing'),
    url(r'^users/', users, name='users'),
    url(r'^api/', include('reports.api.urls')),
]

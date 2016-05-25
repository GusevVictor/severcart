from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^logic.js', TemplateView.as_view(template_name="dhtml/logic.html")),
]

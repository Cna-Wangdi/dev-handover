from django.http import HttpResponse
from django.urls import path
from django.views.generic import TemplateView

from .urls import urlpatterns as api_patterns


def health(request):
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("health/", health),
    *api_patterns,
]

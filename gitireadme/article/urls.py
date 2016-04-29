from django.conf.urls import url, include

from .views import * 



urlpatterns = [
    url(r'^(?P<repo>[0-9a-zA-Z\-\:]+)/(?P<file_name>.+)', article, name="article"),
]

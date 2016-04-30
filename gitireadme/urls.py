from django.conf.urls import include, url
from django.conf import settings

from django.views.static import serve

urlpatterns = [
    url(r'^articles/', include('gitireadme.article.urls')),
]

if settings.DEBUG:
    urlpatterns +=[  
        url(r'^(?P<path>favicon\..*)$',serve, {'document_root': settings.STATIC_ROOT}),
        url(r'^media/(?P<path>.*)$' , serve, {'document_root': settings.MEDIA_ROOT}),
        url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ] 
from django.apps import AppConfig

class AppConfig(AppConfig):
    name = 'gitireadme.spider'
    label = 'gitireadme_spider' 

default_app_config = 'gitireadme.spider.AppConfig'
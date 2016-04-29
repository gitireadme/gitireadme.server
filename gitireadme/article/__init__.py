from django.apps import AppConfig

class AppConfig(AppConfig):
    name = 'gitireadme.article'
    label = 'gitireadme_article' 

default_app_config = 'gitireadme.article.AppConfig'
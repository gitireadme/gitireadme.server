from django.db import models

from gitireadme.utils import getUploadToPath
import datetime

class Article(models.Model):
    name = models.CharField(max_length=255,blank=True,null=True)
    path = models.CharField(max_length=255,blank=True,null=True)

class ArticleAlias(models.Model):
    repo = models.CharField(max_length=255,blank=True,null=True)
    article = models.ForeignKey(Article)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
import os.path
import mimetypes
from django.http import HttpResponse, HttpResponseNotFound
from .models import Article, ArticleAlias 
from gitireadme.spider import spider
# Create your views here.
def article(request,repo,file_name):
    try:
        repo_url=repo.replace(":","/")
        alias = ArticleAlias.objects.filter(repo=repo_url).first()
        if not alias: #find the article
            spider.main(repo_url) 
            alias = ArticleAlias.objects.filter(repo=repo_url).first()
            if not alias:
                return HttpResponseNotFound()
        file_path = settings.MEDIA_ROOT + '/articles/' + alias.article.path +'/'+file_name 
        fsock = open(file_path,"rb")
        file_size = os.path.getsize(file_path)
        print "file size is: " + str(file_size)
        response = HttpResponse(fsock)
        response['Content-Disposition'] = 'attachment; filename=' + file_name            
    except IOError:
        response = HttpResponseNotFound()
    return response
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
import os.path
import mimetypes
from django.http import HttpResponse, HttpResponseNotFound
from .models import Article, ArticleAlias 

# Create your views here.
def article(request,repo,file_name):

    mimetypes.init()
    try:
        #find article, if article exist return file, other wise call spider
        file_path = settings.MEDIA_ROOT + '/articles/' + repo +'/'+file_name 
        fsock = open(file_path,"rb")
        file_size = os.path.getsize(file_path)
        print "file size is: " + str(file_size)
        response = HttpResponse(fsock)
        response['Content-Disposition'] = 'attachment; filename=' + file_name            
    except IOError:
        response = HttpResponseNotFound()
    return response
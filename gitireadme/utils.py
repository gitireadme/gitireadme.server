import datetime, os
from django.conf import settings

def getUploadToPath(instance,filename):
    today = datetime.datetime.today()
    upload_path = 'upload/%d%d/%s' % (today.year,today.month,filename)
    return upload_path

def getFullPath(filename):
    return os.path.join(settings.MEDIA_ROOT,filename)

def jdefault(o):
    '''
        make a default json encoder function, just call to_json method
    '''
    return o.to_JSON()
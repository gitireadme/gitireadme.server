"""
"""
from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
from django.db import connection


class SetHeaderMiddleware(object):
    """
    https://gist.github.com/vstoykov/1390853
    Middleware which prints out a list of all SQL queries done
    for each view that is processed. This is only useful for debugging.
    """
    def __init__(self):
        pass

    def process_response(self, request, response):
        response['Access-Control-Allow-Origin']="*"
        return response
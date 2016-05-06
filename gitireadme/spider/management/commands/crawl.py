from django.core.management.base import BaseCommand

import sys
from gitireadme.spider import spider 

class Command(BaseCommand):
    help = 'usage: python manage.py crawl <repository_url> <dist_path>'

    def add_arguments(self, parser):
        parser.add_argument('repo_url', type=str)
        parser.add_argument('--dist_path', nargs='?', type=str)
        
    def handle(self, *args, **options):
        try: 
            repo_url = options['repo_url']
            dist_path = options['dist_path']
            print repo_url, dist_path
        except:
            print "usage: python spider.py <repository_url> <dist_path>"
            sys.exit()
        spider.main(repo_url,dist_path)
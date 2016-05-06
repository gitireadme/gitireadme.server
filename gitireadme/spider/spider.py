#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
'''
Created on 2 Mar 2016

@author: aaron
'''
from yaml import safe_dump, load
import sys, os,requests, uuid, hashlib, shutil 
import json, codecs, io
from subprocess import Popen
import gitops
from django.conf import settings as s
from gitireadme.article.models import Article as A, ArticleAlias as AA

class Fork(object):
    def __init__(self, raw):
        self.raw = raw
        self.id = raw['id']
        self.name = raw['name']
        self.full_name = raw['full_name']
        self.owner = raw['owner']
        self.description = raw['description']

        self.stars = self.raw['stargazers_count']
        self.watches = self.raw['watchers_count']
        self.branches = None 
        self.parent = None
        return

    def addParent(self, parent):
        self.parent = parent
        return
    def getBranches(self):
        if not self.branches:
            self.branches=[]
            branches_raw = getBranch(self.full_name)
            for b_raw in branches_raw:
                self.branches.append(Branch(b_raw,self))
        else:
            pass
        return self.branches
    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.parent:
            parent=self.parent.id
        else:
            parent=None
        return dict(id=self.id,
                name=self.name,
                description=self.description,
                parent=parent,
                stars=self.stars,
                watches=self.watches,
                owner = self.owner["login"]
                )


class Branch(object):
    def __init__(self,raw,fork):
        self.raw = raw
        self.name = raw['name']
        self.sha = raw['commit']['sha']
        self.fork = fork
        self.full_name = fork.full_name+"/"+self.name
        return

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return dict(name=self.name,
                full_name=self.full_name,
                )

class Commit(object):
    def __init__(self, raw, article):
        self.raw = raw
        self.id = raw["sha"]
        self.parents_dict ={} 
        self.children_dict = {}
        self.branches = [] 
        for p in raw["parents"]:
            parent = article.commits_dict[p["sha"]] 
            self.parents_dict[parent.id]=parent
        
    def getParents(self):
        return self.parents_dict.values()
    def getParentsIds(self):
        parents=self.getParents()
        return [p.id for p in parents]
    def addChildren(self,child):
        if not self.children_dict.has_key(child.id):
            self.children_dict[child.id]=child
        return
    def getChildren(self):
        return self.children_dict.values()
    def addBranch(self, branch):
        self.branches.append(branch)
        return
    def getBranches(self):
        return self.branches;
    def getBranchNames(self):
        branches = self.getBranches()
        return [b.name for b in branches]
    
    def __str__(self):
        return str(self.__unicode__())
    
    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return dict(
                id=self.id,
                parents=self.getParentsIds(),
                branches=self.getBranchNames(),
                username=self.raw["commit"]["author"]["name"],
                date=self.raw["commit"]["author"]["date"],
                    )

class Article(object):
    def __init__(self,raw):
        #get root to represent article
        self.root = getRoot(raw)
        self.name = self.root.name
        self.full_name = self.root.full_name 
        self.file_name = self.full_name.replace("/",":")
        self.commits_dict = {} 
        self.forks = []
    
    def addCommit(self,commit): 
        if not self.commits_dict.has_key(commit.id):
            self.commits_dict[commit.id]=commit
        return
    def getCommits(self):
        return self.commits_dict.values()
    
    def getForks(self):
        return self.forks
    
    def crawl(self):
        # get all forks recursively
        self.fetchForks(self.root)
        for fork in self.forks:
            branches=fork.getBranches()
            for branch in branches:
                commits_url = fork.raw["commits_url"].replace("{/sha}","?sha="+branch.name)

                print commits_url
                commits_raw = getUrl(commits_url)
                #assume order by time
                for c_raw in reversed(commits_raw):
                    if self.commits_dict.has_key(c_raw["sha"]):
                        continue
                    commit = Commit(c_raw,self)
                    self.addCommit(commit)

                #add branches to the commit 
                commit = self.commits_dict[branch.sha]
                commit.addBranch(branch)
           
        #set commit children
        for commit in self.getCommits():
            for parent in commit.getParents(): 
                parent.addChildren(commit)

    
    def fetchForks(self,fork): 
        '''
            get all forks recursively
        '''
        #TODO considering pagination
        self.forks.append(fork)
        if fork.raw["forks_count"] > 0 :
            url = fork.raw['forks_url']
            forks_raw = getUrl(url)
            for f_raw in forks_raw:
                f = Fork(f_raw)
                f.parent=fork
                self.fetchForks(f)
 


class ArticleSpider(object):
    '''
    crawl articles from github user or organization
    '''
    def __init__(self, repository_url,repo_path, dist_path):
        '''
        Constructor
        '''
        self.dist_path = dist_path
        self.repository_url = repository_url
        self.repo_path = repo_path
        self.article = '' 
         
    def crawl(self):
        print self.repository_url
        repository_info = getRepo(self.repository_url)
        print repository_info
        self.article = Article(repository_info)
        self.article.crawl()

    def render(self):
        self.pull_all()
        self.render_meta()
        self.render_articles()

    def store(self):
        #save article
        article = A()
        article.name = self.article.name
        article.path = self.article.file_name
        article.save()
        #save article alias
        for fork in self.article.forks:
            articleAlias = AA()
            articleAlias.article=article
            articleAlias.repo = fork.full_name
            articleAlias.save()
        return
    
    def pull_all(self):
        
        repo_path=os.path.join(self.repo_path,self.article.file_name)

        for commit in self.article.getCommits():
            children =commit.getChildren()
            #only pull the leaf commit
            if len(children)>0:
                continue
            branches = commit.getBranches()
            if len(branches)==0:
                continue
            branch = branches[0] 

            username=branch.fork.owner['login']
            repo_name=branch.fork.name
            branch_name=branch.name
            gitops.gitFetch(repo_path,username,repo_name,branch_name)
        return

    def render_articles(self):

        repo_path=os.path.join(self.repo_path,self.article.file_name)
        dist_path=os.path.join(self.dist_path,self.article.file_name)
        if not os.path.exists(dist_path):
            os.makedirs(dist_path)

        for commit in self.article.getCommits():
            file_path=os.path.join(dist_path,commit.id+'.md')
            if not os.path.exists(file_path):
                print "generate file %s" % file_path
                gitops.gitStore(repo_path,commit.id,file_path)
        return 
    
    def render_meta(self):
        dist_path=os.path.join(self.dist_path,self.article.file_name)
        if not os.path.exists(dist_path):
            os.makedirs(dist_path)

        commits = [c.__repr__() for c in self.article.getCommits()]
        forks = [f.__repr__() for f in self.article.getForks()]
        meta = dict(commits=commits, forks=forks)


        #to yaml
        file_yaml = codecs.open(os.path.join(dist_path,"meta.yml"),"w",encoding="utf-8")
        out = safe_dump(meta,allow_unicode=True)
        file_yaml.write(out.decode("utf-8"))
        file_yaml.close()
        
        #to json 
        file_json = codecs.open(os.path.join(dist_path,"meta.json"),"w",encoding="utf-8")
        out = json.dumps(meta)
        file_json.write(out.decode("utf-8"))
        file_json.close()
        return

def getRoot(raw):
    if raw['fork'] == True:
        return Fork(raw['source'])
    else:
        return Fork(raw)

def emptyDirectory(path):                
    os.system("rm -rf dist/%s/*" % path)

def getOrgsRepo(orgs_name):                     
    url = s.SPIDER_GITHUB_API+"orgs/"+orgs_name+"/repos"        
    return getUrl(url)        

def getRepo(repository):                     
    url = s.SPIDER_GITHUB_API+"repos/"+repository        
    return getUrl(url)        

def getBranch(repository):                     
    url = s.SPIDER_GITHUB_API+"repos/"+repository+"/branches"        
    return getUrl(url)     

def getUrl(url):
    if url.find("?")== -1:
        url+="?1=1"
    url+="&client_id="+s.SPIDER_CLIENT_ID+"&client_secret="+s.SPIDER_CLIENT_SECRET
    r = requests.get(url)
    if not r.status_code == 200:
        print "error return code", r.status_code
        return None
    else:
        return r.json()

def main(repo_url,dist_path=None):

    if not dist_path:
        dist_path = os.path.join(s.MEDIA_ROOT,s.SPIDER_DIST_PATH) 

    repo_path = s.SPIDER_REPO_PATH

    if not os.path.exists(dist_path):
        os.makedirs(dist_path)
    if not os.path.exists(repo_path):
        print "repo path not exists"
        os.makedirs(repo_path)

    #print repository_url
    spider = ArticleSpider(repo_url, repo_path, dist_path)
    spider.crawl()
    spider.render()
    spider.store() 

 
if __name__ == "__main__":
   
    try: 
        repo_url = sys.argv[1]
        dist_path = sys.argv[2]
    except:
        print "usage: python spider.py <repository_url> <dist_path>"
        sys.exit()
    main(repo_url,dist_path)
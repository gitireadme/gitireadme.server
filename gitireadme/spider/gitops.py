import os 
from django.conf import settings as s

def gitFetch(repo_path, username,repo_name,branch_name):
	'''
		directory: target directory
		url: git fetch url from github
	'''
	print "fetch "+repo_path
	remote_url = s.SPIDER_GITHUB+username+"/"+repo_name+".git"
	if not os.path.exists(repo_path):
		os.makedirs(repo_path)
		os.system("cd %s && git init" % repo_path)

	remote_list = os.popen("cd %s && git remote" % repo_path).read().split("\n")

	if not username in remote_list:
		os.system("cd %s && git remote add %s %s" % (repo_path, username,remote_url))
	os.system("cd %s && git fetch %s %s" % (repo_path, username,branch_name))

def gitStore(repo_path,commit_sha, file_path):
	'''
		dir: target directory
		article_name: repository name on github
		commit_id: hashed commit id on github
	'''
	print "repo_path "+repo_path
	os.system("cd %s && git checkout %s && cp README.md %s" % (repo_path, commit_sha, file_path))

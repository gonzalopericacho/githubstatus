import gevent.monkey
gevent.monkey.patch_all()
import os
import gevent
import requests
import requests.packages.urllib3
from tabulate import tabulate



requests.packages.urllib3.disable_warnings()
TOKEN = os.getenv("GITHUB_TOKEN")

def status(i):
    '''
    gives the status of a given branch of a repo
    '''
    state=u'\u2713' #success
    for status in threads[i].value["statuses"]:
        if status["state"] == "failure":
            state=u'\u2717' #failure
            break
        elif status["state"] == "pending":
            state=u'\u2022'  #pending
    return state

def notes(i):
    notes=""
    if len(threads[i+6].value)!=0 and \
        threads[i+6].value[0]["commit"]["sha"]!=threads[i+7].value["object"]["sha"]:
        notes+="Release missing, "
    if threads[i+3].value["behind_by"]>0:
        notes+="Staging needs rebasing, "
    return notes[:-2]
 
def make_request(path, method="GET"):
    url = "https://api.github.com%s" % path if not path.startswith("http") else path
    r = requests.request(method, url, headers={"Accept": "application/vnd.github.v3+json",
                                               "Authorization": "token %s" % TOKEN})
    json=r.json()
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as error:
        if "releases/latest" in path: #no release on repo
            json["name"]= "-"
        else:
            raise
    return json

def initial_request(path, method="GET"):
    url = "https://api.github.com%s" % path if not path.startswith("http") else path
    r = requests.request(method, url, headers={"Accept": "application/vnd.github.v3+json",
                                               "Authorization": "token %s" % TOKEN})
    json=r.json()
    r.raise_for_status()
    try:
    	pages=r.headers["link"].split(",")[1].split(";")[0][:-1].split("=")[-1]
    except:
    	pages=1
    return json,pages

if __name__ == '__main__':

    table = []
    queries=[]
    major_repos=[]
    minor_repos=[]
    repos,pages=initial_request("/user/repos")
    for page in range(1,int(pages)+1):
    	queries.append("/user/repos?per_page=30&page=%s" %page)

   	threads = [gevent.spawn( make_request, query) for query in queries]
    gevent.joinall(threads, raise_error=False)

    for repos in threads:
    	for repo in repos.value:
	        if repo["owner"]["type"]!= "User" and not "DEPRECATED" in repo["description"]:
	            if (repo["default_branch"]=="staging"):
	                major_repos.append(repo["full_name"].encode("ascii","ignore"))
	            else:
	                minor_repos.append(repo["full_name"].encode("ascii","ignore"))
    queries=[]
    for repo in major_repos:
        queries.extend(["/repos/%s" % repo,
                        "/repos/%s/releases/latest" % repo,
                        "/repos/%s/pulls" % repo,
                        "/repos/%s/compare/master...staging" % repo,
                        "/repos/%s/commits/master/status" % repo,
                        "/repos/%s/commits/staging/status" % repo,
                        "/repos/%s/tags" % repo,
                        "/repos/%s/git/refs/heads/master" % repo])

    for repo in minor_repos:
        queries.extend(["/repos/%s" % repo,
                        "/repos/%s/pulls" % repo])

    threads = [gevent.spawn( make_request, query) for query in queries]
    gevent.joinall(threads, raise_error=False)
    
    i=0    
    for repo in major_repos:
        table.append([repo,
                     threads[i+1].value["name"],
                     str(threads[i+3].value["behind_by"])+"/"+ str(threads[i+3].value["ahead_by"]),
                     threads[i].value["open_issues_count"],
                     len(threads[i+2].value),
                     status(i+4)+"   "+status(i+5),
                     notes(i)]) # append to table
        i=i+8
    print tabulate(table, headers=["Repo", "Release", "Staging","Issues","PR","m / s","Notes"])
    
    table = []
    for repo in minor_repos: 
        table.append([repo,threads[i].value["open_issues_count"],
                     len(threads[i+1].value),
                     threads[i].value["stargazers_count"],
                     threads[i].value["forks_count"]])
        i+=2
    table.sort(key=lambda x: x[3],reverse=True)
    print tabulate(table, headers=["Repo","Issues","PR","Stars","Forks"])






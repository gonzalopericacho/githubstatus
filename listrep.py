import os
import requests
import requests.packages.urllib3
from tabulate import tabulate
from threading import Thread

requests.packages.urllib3.disable_warnings()
TOKEN = os.getenv("GITHUB_TOKEN")

def make_request(path, method="GET"):
    url = "https://api.github.com%s" % path if not path.startswith("http") else path
    r = requests.request(method, url, headers={"Accept": "application/vnd.github.v3+json",
                                               "Authorization": "token %s" % TOKEN})
    json=r.json()
    if r.status_code != requests.codes.ok:
        if "releases/latest" in path: #no release on repo
            json["name"]= "Not found"
        else:
            r.raise_for_status()
    return json

if __name__ == '__main__':
	mylist=[]
	for repo in make_request("/user/repos?per_page=200"):
		if repo["owner"]["type"]!= "User": 
			mylist.append(repo["name"].encode("ascii","ignore"))
	print mylist
	print len(mylist)
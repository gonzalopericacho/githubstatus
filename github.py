import os
import requests
import requests.packages.urllib3
from tabulate import tabulate
 
requests.packages.urllib3.disable_warnings()
 
 
TOKEN = os.getenv("GITHUB_TOKEN")
 
repos = ["tutumcloud/tutum-app","tutumcloud/events", "tutumcloud/weave-daemon", "tutumcloud/metrics"]
jumpstarts = ["tutumcloud/newrelic-agent","tutumcloud/haproxy", "tutumcloud/redis", "tutumcloud/mongodb",
			"tutumcloud/hello-world"]
 
def make_request(path, method="GET"):
    url = "https://api.github.com%s" % path if not path.startswith("http") else path
    r = requests.request(method, url, headers={"Accept": "application/vnd.github.v3+json",
                                               "Authorization": "token %s" % TOKEN})
    r.raise_for_status()
    return r.json()
 
if __name__ == '__main__':

    table = []
    for repo in repos:
    	print "scanning "+repo
        info = make_request("/repos/%s" % repo)
        release = make_request("/repos/%s/releases/latest" % repo)
        pr=len(make_request("/repos/%s/pulls" % repo))
        c=make_request("/repos/%s/compare/master...staging" % repo)
        table.append([repo, release["name"],str(c["behind_by"])+"/"+str(c["ahead_by"]), info["open_issues_count"],pr]) # append to table
    print tabulate(table, headers=["Repo", "Release", "Staging","Issues","PR"])


    table = []
    for repo in jumpstarts:
    	print "scanning "+repo
    	info = make_request("/repos/%s" % repo)
    	pr=len(make_request("/repos/%s/pulls" % repo))
    	table.append([repo,info["open_issues_count"],pr,info["stargazers_count"],info["forks_count"]])
    print tabulate(table, headers=["Repo","Issues","PR","Stars","Forks"])




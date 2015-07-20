import os
import requests
import requests.packages.urllib3
from tabulate import tabulate
from threading import Thread


requests.packages.urllib3.disable_warnings()
TOKEN = os.getenv("GITHUB_TOKEN")
 
repos = ["tutumcloud/api-docs","tutumcloud/builder","tutumcloud/cleanup",
        "tutumcloud/cli","tutumcloud/docker-registry","tutumcloud/docker-update",
        "tutumcloud/events","tutumcloud/go-tutum","tutumcloud/metrics",
        "tutumcloud/ntpd","tutumcloud/python-tutum","tutumcloud/stackfiles",
        "tutumcloud/support-docs","tutumcloud/tutum-agent","tutumcloud/tutum-app",
        "tutumcloud/tutum-ui","tutumcloud/tutum-live","tutumcloud/weave-daemon"]

jumpstarts = ["tutumcloud/apache-php","tutumcloud/authorizedkeys","tutumcloud/btsync",
              "tutumcloud/couchdb","tutumcloud/curl","tutumcloud/datadog-agent",
              "tutumcloud/dockup","tutumcloud/elasticsearch","tutumcloud/glassfish",
              "tutumcloud/grafana","tutumcloud/haproxy","tutumcloud/hello-world",
              "tutumcloud/homebrew","tutumcloud/influxdb","tutumcloud/jboss",
              "tutumcloud/labelizer","tutumcloud/lamp","tutumcloud/mariadb",
              "tutumcloud/memcached","tutumcloud/mongodb","tutumcloud/mysql",
              "tutumcloud/nginx","tutumcloud/ngrok-server","tutumcloud/postgresql",
              "tutumcloud/python-social-auth","tutumcloud/rabbitmq","tutumcloud/redis",
              "tutumcloud/riak","tutumcloud/slate","tutumcloud/syslogger","tutumcloud/tomcat",
              "tutumcloud/tutum-centos","tutumcloud/tutum-debian","tutumcloud/tutum-fedora",
              "tutumcloud/tutum-ubuntu","tutumcloud/unixbench","tutumcloud/varnish",
              "tutumcloud/wordpress","tutumcloud/wordpress-stackable"]
 
def make_request(path, method="GET"):
    url = "https://api.github.com%s" % path if not path.startswith("http") else path
    r = requests.request(method, url, headers={"Accept": "application/vnd.github.v3+json",
                                               "Authorization": "token %s" % TOKEN})
    json=r.json()
    if r.status_code != requests.codes.ok:
        if "releases/latest" in path: #no release on repo
            json["name"]= "-"
        else:
            r.raise_for_status()
    return json

def process_range(queries, store=None):
    if store is None:
        store = {}
    for path in queries:
        store[path] = make_request(path)
    return store

def threaded_process_range(nthreads, queries):
    store = {}
    threads = []
    # create the threads
    for i in range(nthreads):
        ids = queries[i::nthreads]
        t = Thread(target=process_range, args=(ids,store))
        threads.append(t)

    # start the threads
    [ t.start() for t in threads ]
    # wait for the threads to finish
    [ t.join() for t in threads ]
    return store

def status(repo,branch):
    '''
    gives the status of a given branch of a repo
    '''
    state=u'\u2713' #success
    for status in store["/repos/%s/commits/%s/status" % (repo,branch)]["statuses"]:
        if status["state"] == "failure":
            state=u'\u2717' #failure
            break
        elif status["state"] == "pending":
            state=u'\u2022'  #pending
    return state

def notes(repo):
    notes=""
    if len(store["/repos/%s/tags" % repo])!=0 and \
        store["/repos/%s/tags" % repo][0]["commit"]["sha"]!=store["/repos/%s/git/refs/heads/master" % repo]["object"]["sha"]:
        notes+="Release missing, "
    if store["/repos/%s/compare/master...staging" % repo]["behind_by"]>0:
        notes+="Staging needs rebasing, "
    if store["/repos/%s/compare/master...staging" % repo]["ahead_by"]>0:
        notes+="Pending release, "
    return notes[:-2]

if __name__ == '__main__':

    table = []
    queries=[]
    for repo in repos:
    	queries.extend(["/repos/%s" % repo,
                        "/repos/%s/releases/latest" % repo,
                        "/repos/%s/pulls" % repo,
                        "/repos/%s/compare/master...staging" % repo,
                        "/repos/%s/commits/master/status" % repo,
                        "/repos/%s/commits/staging/status" % repo,
                        "/repos/%s/tags" % repo,
                        "/repos/%s/git/refs/heads/master" % repo])
    for repo in jumpstarts:
        queries.extend(["/repos/%s" % repo,
                        "/repos/%s/pulls" % repo])
    
    store=threaded_process_range(10,queries)
    
    for repo in repos:

        table.append([repo,
        			 store["/repos/%s/releases/latest" % repo]["name"],
        			 str(store["/repos/%s/compare/master...staging" % repo]["behind_by"])+"/"+str(store["/repos/%s/compare/master...staging" % repo]["ahead_by"]),
        			 store["/repos/%s" % repo]["open_issues_count"],
        			 len(store["/repos/%s/pulls" % repo]),
                     status(repo,"master")+"   "+status(repo,"staging"),
                     notes(repo)]) # append to table
    print tabulate(table, headers=["Repo", "Release", "Staging","Issues","PR","m / s","Notes"])

    table = []
    for repo in jumpstarts:	
        table.append([repo,store["/repos/%s" % repo]["open_issues_count"],
                     len(store["/repos/%s/pulls" % repo]),
                     store["/repos/%s" % repo]["stargazers_count"],
                     store["/repos/%s" % repo]["forks_count"]])
        table.sort(key=lambda x: x[3],reverse=True)
    print tabulate(table, headers=["Repo","Issues","PR","Stars","Forks"])
    


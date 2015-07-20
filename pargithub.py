import gevent.monkey
gevent.monkey.patch_all()
import os
import gevent
import requests
import requests.packages.urllib3
from tabulate import tabulate



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
    if threads[i+3].value["ahead_by"]>0:
        notes+="Pending release, "
    return notes[:-2]
 
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

    threads = [gevent.spawn( make_request, query) for query in queries]
    gevent.joinall(threads, raise_error=False)
    
    i=0    
    for repo in repos:

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
    for repo in jumpstarts: 
        table.append([repo,threads[i].value["open_issues_count"],
                     len(threads[i+1].value),
                     threads[i].value["stargazers_count"],
                     threads[i].value["forks_count"]])
        i+=2
    table.sort(key=lambda x: x[3],reverse=True)
    print tabulate(table, headers=["Repo","Issues","PR","Stars","Forks"])






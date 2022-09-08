import requests
import json
import os
import pandas as pd


def query_jira_agile(site, auth, param, page_size=500):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    cert = os.path.abspath(os.path.join(os.path.dirname(__file__), 'IntelSHA256RootCA-base64.crt'))

    url = "https://" + site + "/rest/agile/1.0/" + param
    http_res = requests.request("GET", url, headers=headers, verify=cert)
    res = json.loads(http_res.text)
    res_size = len(res['values'])

    query = {
        'startAt': 0,
        'maxResults': page_size
    }
    # API operations
    page_index = 0
    while (res_size == page_size):
        # API operations
        page_index = page_index + page_size
        query['startAt'] = page_index
        http_res = requests.request("GET", url, headers=headers, params=query, verify=cert)
        res0 = json.loads(http_res.text)
        res['values'] = res['values'] + res0['values']
        res_size = len(res0['values'])
        print("len(res['values'])", res_size)
    return res

def res_to_sprint(res):
    sprints = []
    sprint = {}
    for i in range(len(res['values'])):
        sprint['sprint_name'] = res['values'][i]['name']
        sprint['sprint_id'] = res['values'][i]['id']
        sprints.append(sprint)
        sprint = {}
    return sprints

fname = "tmp/sprintss.csv"
jirasite = "jira.devtools.intel.com"
auth = "Bearer " + os.environ['cheahchr-jira-prod-pat']
jira_boards = ['31967','38314']
sprints = []
# jira_boardid = 31967
for jira_boardid in jira_boards:
    param = "board/{}/sprint".format(jira_boardid)
    res = query_jira_agile(jirasite, auth, param)
    sprints += res_to_sprint(res)

df_sprints = pd.DataFrame.from_records(sprints)
df_sprints.to_csv(fname, mode='w', index=False, header=True)


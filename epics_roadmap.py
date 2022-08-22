import requests
import json
import os
import pandas as pd


def query_jira(site, auth, jql, fields, page_size=500):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    cert = os.path.abspath(os.path.join(os.path.dirname(__file__), 'IntelSHA256RootCA-base64.crt'))

    query = {
        'jql': jql,
        'fields': fields,
        'startAt': 0,
        'maxResults': page_size
    }


    url = "https://" + site + "/rest/api/2/search"
    http_res = requests.request("GET", url, headers=headers, params=query, verify=cert)
    res = json.loads(http_res.text)
    res_size = len(res['issues'])


    # API operations
    page_index = 0
    while (res_size == page_size):
        # API operations
        page_index = page_index + page_size
        query['startAt'] = page_index
        http_res = requests.request("GET", url, headers=headers, params=query, verify=cert)
        res0 = json.loads(http_res.text)
        res['issues'] = res['issues'] + res0['issues']
        res_size = len(res0['issues'])
        print("len(res['issues'])", res_size)
    return res

def res_to_issues(res):
    issues = []
    issue = {}
    for i in range(len(res['issues'])):
        issue['issue'] = res['issues'][i]['key']
        issue['summary'] = res['issues'][i]['fields']['summary']
        issue['issuetype'] = res['issues'][i]['fields']['issuetype']['name']
        issue['project'] = res['issues'][i]['fields']['project']['key']
        issue['project_name'] = res['issues'][i]['fields']['project']['name']

        issue['reporter_name'] = res['issues'][i]['fields']['reporter']['name']
        issue['reporter_displayName'] = res['issues'][i]['fields']['reporter']['displayName']
        issue['assignee_displayName'] = None
        issue['assignee_name'] = None
        if res['issues'][i]['fields']['assignee']:
            issue['assignee_displayName'] = res['issues'][i]['fields']['assignee']['displayName']
            issue['assignee_name'] = res['issues'][i]['fields']['assignee']['name']
        issue['epic_link'] = res['issues'][i]['fields']['customfield_11900']
        issue['duedate'] = res['issues'][i]['fields']['duedate']
        issue['created'] = res['issues'][i]['fields']['created']
        issue['status'] = res['issues'][i]['fields']['status']['name']
        issue['sprint'] = None
        issue['sprint_startDate'] = None
        issue['sprint_endDate'] = None
        if res['issues'][i]['fields']['customfield_11605']:
            customfield_11605 = res['issues'][i]['fields']['customfield_11605'][0].split(
                ',')
            issue['sprint'] = customfield_11605[3][5:13] + \
                customfield_11605[3][16:18]
            issue['sprint_startDate'] = customfield_11605[4].split('=')[1]
            issue['sprint_endDate'] = customfield_11605[5].split('=')[1]

        issues.append(issue)
        issue = {}
    return issues

def res_to_epics(res):
    issues = []
    issue = {}
    for i in range(len(res['issues'])):
        issue['epic_link'] = res['issues'][i]['key']
        issue['epic_summary'] = res['issues'][i]['fields']['summary']
        issues.append(issue)
        issue = {}
    return issues

fname = "tmp/issues.csv"
jirasite = "jira.devtools.intel.com"
auth = "Bearer " + os.environ['cheahchr-jira-prod-pat']

projects = ['TWC3149','TWC4618']
jql_projects = ','.join(['TWC3149','TWC4618'])
jql = 'project in ({}) and status not in (Done, Canceled) and issuetype in (Story,Bug)'.format(jql_projects)
jira_fields = 'key,summary,issuetype,reporter,created,updated,assignee,status,project,customfield_11900,duedate,customfield_11605'

res = query_jira(jirasite, auth, jql, jira_fields)
issues = res_to_issues(res)
df_issues = pd.DataFrame.from_records(issues)

# select unique not empty epic links 
epic_links = df_issues[df_issues['epic_link'].notna()]['epic_link'].unique().tolist()
jql = 'issue in (' + ','.join(epic_links) + ')'
auth = "Bearer " + os.environ['cheahchr-jira-prod-pat']
# jql = 'project in (TWC3149,TWC4618) and status not in (Done, Canceled) and issuetype in (Story,Bug)'
jira_fields = 'key,summary'
res = query_jira(jirasite, auth, jql, jira_fields)

epics = res_to_epics(res)
df_epics = pd.DataFrame.from_records(epics)
df_issues_final = pd.merge(df_issues, df_epics, on='epic_link', how ="left")

df_issues_final.to_csv(fname, mode='w', index=False, header=True)


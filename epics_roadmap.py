import json, os, sys
import requests
import pandas as pd


def query_jira(site, auth, jql, fields, page_size=500):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }
    cert = os.path.abspath(os.path.join(os.path.dirname(
        __file__), 'IntelSHA256RootCA-base64.crt'))

    query = {
        'jql': jql,
        'fields': fields,
        'startAt': 0,
        'maxResults': page_size
    }

    url = "https://" + site + "/rest/api/2/search"
    http_res = requests.request(
        "GET", url, headers=headers, params=query, verify=cert)
    if http_res.status_code == 200:
        res = json.loads(http_res.text)
        res_size = len(res['issues'])
        # API operations
        page_index = 0
        while (res_size == page_size):
            # API operations
            page_index = page_index + page_size
            query['startAt'] = page_index
            http_res = requests.request(
                "GET", url, headers=headers, params=query, verify=cert)
            res0 = json.loads(http_res.text)
            res['issues'] = res['issues'] + res0['issues']
            res_size = len(res0['issues'])
        return res
    else:
        return None


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
        issue['story_points'] = res['issues'][i]['fields']['customfield_11204']
        issue['duedate'] = res['issues'][i]['fields']['duedate']
        issue['created'] = res['issues'][i]['fields']['created'][0:10]
        issue['status'] = res['issues'][i]['fields']['status']['name']
        issue['sprint'] = None
        issue['sprint_startDate'] = None
        issue['sprint_endDate'] = None
        if res['issues'][i]['fields']['customfield_11605']:
            customfield_11605 = res['issues'][i]['fields']['customfield_11605'][0].split(
                ',')
            issue['sprint'] = customfield_11605[3][5:13] + \
                customfield_11605[3][16:18]
            issue['sprint_startDate'] = customfield_11605[4].split('=')[
                1][0:10]
            issue['sprint_endDate'] = customfield_11605[5].split('=')[1][0:10]
            if issue['duedate'] is None:
                issue['sort_date'] = issue['sprint_endDate']
            else:
                issue['sort_date'] = issue['duedate']
        issues.append(issue)
        issue = {}
    return issues


def res_to_epics(res):
    issues = []
    issue = {}
    for i in range(len(res['issues'])):
        issue['epic_link'] = res['issues'][i]['key']
        issue['epic_summary'] = res['issues'][i]['fields']['summary']
        issue['capability_displayName'] = res['issues'][i]['fields']['customfield_36601']
        try:
            if issue['epic_link'] is None or len(issue['epic_link']) < 3:
                issue['epic_displayName'] = None
            else:
                issue['epic_displayName'] = '{}: {}'.format(
                    issue['epic_link'], issue['epic_summary'])
        except:
            print("error i:{}, epic link: {}".format(i, issue['epic_link']))
        issues.append(issue)
        issue = {}
    return issues


def get_issues_by_projects(query_jira, res_to_issues, jirasite, auth, projects=None):
    # jql = 'project in ({}) and status not in (Canceled) and issuetype in (Story,Bug)'.format(jql_params)
    if projects is None:
        return None
    else:
        issues = []
        jira_fields = 'key,summary,issuetype,reporter,created,updated,assignee,status,project,customfield_11900,customfield_11204,duedate,customfield_11605'
        for project in projects:
            jql = 'project={} and status not in (Canceled) and issuetype in (Story,Bug)'.format(project)
            res = query_jira(jirasite, auth, jql, jira_fields)
            issues += res_to_issues(res)
        # jql = 'project in ({}) and status not in (Canceled) and issuetype in (Story,Bug)'.format(','.join(projects))
        # res = query_jira(jirasite, auth, jql, jira_fields)
        # issues = res_to_issues(res)
        return issues


def get_issue_epic_detail(query_jira, res_to_epics, jirasite, auth, jql_params):
    jql = 'issue in (' + ','.join(jql_params) + ')'
    jira_fields = 'key,summary,customfield_36601'
    res = query_jira(jirasite, auth, jql, jira_fields)
    epics = res_to_epics(res)
    return epics

config_file = os.path.join(os.path.dirname(sys.argv[0]), 'epics_roadmap_config.json')
with open(config_file) as f:
   config = json.load(f)

fname = os.path.join(os.path.dirname(sys.argv[0]), config['output']['filename'])
jirasite = config['jira']['site']
if config['jira']['token_env_name']:
    auth = "Bearer " + os.environ[config['jira']['token_env_name']]
elif config['jira']['token']:
    auth = "Bearer " + config['jira']['token']
# auth = "Bearer " + os.environ['cheahchr-jira-prod-pat']

projects = ['TWC3149', 'TWC4618']
projects = config['jira']['projects']
issues = get_issues_by_projects(
    query_jira, res_to_issues, jirasite, auth, projects)
df_issues = pd.DataFrame.from_records(issues)

# select unique not empty epic links
epic_links = df_issues[df_issues['epic_link'].notna()
                       ]['epic_link'].unique().tolist()
epics = get_issue_epic_detail(
    query_jira, res_to_epics, jirasite, auth, epic_links)
df_epics = pd.DataFrame.from_records(epics)

# join issues and epics by epics link
df_issues_final = pd.merge(df_issues, df_epics, on='epic_link', how="left")
df_issues_final.to_csv(fname, mode='w', index=False, header=True)

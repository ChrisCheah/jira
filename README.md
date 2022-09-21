# Getting Started


## Setting Up
Using Powershell
1. Download
``` powershell
git clone https://github.com/ChrisCheah/jira.git
cd jira
python -m venv env
env\Scripts\activate.ps1
```
2. Install  
``` powershell
pip install --proxy=http://proxy-chain.intel.com:911 -r requirements.txt
```
`--proxy=http://proxy-chain.intel.com:911` is needed when Intel VPN is turned on   

## Usage
### Sprint Planning.xlsm
#### US tree
A pivot table that provide a tree view of user stories group by feature/epic and capacility over sprints

Configure `epics_roadmap_config.json` to use `US tree`   
1. Update list of projects
`project`: list of JIRA project id
2. Provide authetication token
`token`: JIRA personal access token 
or 
`token_env_name`: OS environment variable that store the JIRA personal access token

To refresh Sprint Planning.xlsm, click `Data` -> `Refresh All`






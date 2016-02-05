import dateutil.parser
from settings import CREDENTIALS, PROJECTS, UPDATED_SINCE_HOURS
from jiracopy import JiraLogCopier

jira_log_copier = JiraLogCopier(CREDENTIALS, PROJECTS, UPDATED_SINCE_HOURS)
jira_log_copier.copy_worklogs()
print "Done."

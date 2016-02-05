import dateutil.parser
from settings import CREDENTIALS, PROJECTS, UPDATED_SINCE
from jiracopy import JiraLogCopier

jira_log_copier = JiraLogCopier(CREDENTIALS, PROJECTS, UPDATED_SINCE)
jira_log_copier.copy_worklogs()
print "Done."

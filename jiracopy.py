import dateutil.parser
import datetime
from dateutil.tz import tzutc
from jira import JIRA
from jira.exceptions import JIRAError

class JiraLogCopier(object):
    source = None
    destination = None
    projects = None
    credentials = None
    updated_since = None

    def __init__(self, credentials, projects, updated_since):
        self.projects = projects
        self.credentials = credentials
        self.updated_since = updated_since

    def authenticate(self, username, password, server):
        try:
            print('Logging in to %s' % (server))
            jira = JIRA(basic_auth=(username, password), server=server)
        except JIRAError, ex:
            return None
        return jira

    def createFromJQL(self, frm):
        # Only get logs from yesterday until today.
        jql = 'project = \'%s\' and updated < endOfDay() AND updated > -%sh ORDER BY updated DESC' % (frm, self.updated_since)
        # Strip Session keyword.
        return jql.replace('Session', '\'Session\'')

    def get_source_issues(self):
        """
        Retrieve issues from source JIRA
        """
        self.source = self.authenticate(
                self.credentials['from']['username'],
                self.credentials['from']['password'],
                self.credentials['from']['server']
                )
        if self.source is not None:
            for frm, to in self.projects.iteritems():
                print 'Getting worklogs for %s' % (frm,)

                jql = self.createFromJQL(frm)

                print(jql)

                return self.source.search_issues(jql)
        else:
            print 'Unable to connect to %s.' % (self.credentials['from']['server'],)

        return None

    def createToJQL(self, issue, to):
        summary_q = '[%s]' % (issue.key,)
        for o, r in [('?', '\\\\?'), ('[', '\\\\['), (']', '\\\\]')]:
            summary_q = summary_q.replace(o, r)

        return 'project = \'%s\' and summary ~ \'%s\'' % (to.split(' > ')[0], summary_q)

    def manage_logs(self, frm, to, issue, logs):
        """
        Manage worklogs.
        """
        self.destination = self.authenticate(self.credentials['to']['username'], self.credentials['to']['password'], self.credentials['to']['server'])

        if self.destination is not None:
            try:
                jql = self.createToJQL(issue, to)

                print(jql)

                with_local = False
                for local_issue in self.destination.search_issues(jql):
                    print(local_issue)

                    with_local = True
                    self.insert_logs(to, local_issue, issue, self.destination.worklogs(local_issue), logs)

                if not with_local:
                    print("No local issue.")
                    self.insert_logs(to, None, issue, [], logs, True)
            except Exception, ex:
                print(ex)
        else:
            print 'Unable to connect to %s.' % (self.credentials['to']['server'],)

    def insert_logs(self, project_key, local_issue, remote_issue, dst_worklogs, src_worklogs, is_new=False):
        """
        Insert worklogs to destination JIRA
        """
        if is_new:
            local_issue = self.create_issue(project_key, remote_issue)
            if local_issue is not None:
                for log in src_worklogs:
                    try:
                        local_log = self.destination.add_worklog(
                                issue=local_issue,
                                timeSpent=log.timeSpent,
                                started=dateutil.parser.parse(log.started),
                                comment=log.comment
                                )
                        print ('Worklog successfully added.')
                    except Exception, ex:
                        print(ex)
        else:
            for log in filter(
                    lambda x: dateutil.parser.parse(x.started) >= (datetime.datetime.now(tzutc()) - datetime.timedelta(hours=self.updated_since)),
                    src_worklogs
                    ):
                found = filter(lambda x:
                        log.comment == x.comment
                        and log.timeSpent == x.timeSpent
                        and dateutil.parser.parse(log.started) == dateutil.parser.parse(x.started),
                        dst_worklogs)
                if len(found) == 0:
                    print(log.comment)
                    local_log = self.destination.add_worklog(
                            issue=local_issue,
                            timeSpent=log.timeSpent,
                            started=dateutil.parser.parse(log.started),
                            comment=log.comment
                            )
                    print ('Worklog successfully added.')
                else:
                    print('Existing worklog found.')

    def create_issue(self, project_key, remote_issue):
        """
        Create an issue if not found.
        """
        try:
            project = self.destination.project(project_key.split(' > ')[0])
            issue_dict = {
                    'project': {'id': project.id},
                    'summary': '[%s] %s' % (remote_issue.key, remote_issue.fields.summary),
                    'description': 'Copy of %s/browse/%s' % (self.credentials['from']['server'], remote_issue.key),
                    'issuetype': {'id': 3}, # Task
                    'assignee': {'name': self.destination.current_user()}
                    }
            print('Creating new issue.')
            return self.destination.create_issue(fields=issue_dict)
        except Exception, ex:
            # FIXME: More specific exception.
            print(ex)
            return None

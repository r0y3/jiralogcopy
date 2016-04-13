from settings import CREDENTIALS, PROJECTS, UPDATED_SINCE_HOURS
from jiracopy import JiraLogCopier
from worker import JiraWorker
from Queue import Queue
from time import time
import multiprocessing

ts = time()
jira_log_copier = JiraLogCopier(CREDENTIALS, PROJECTS, UPDATED_SINCE_HOURS)
queue = Queue()
for x in range(multiprocessing.cpu_count()):
    worker = JiraWorker(queue, jira_log_copier)
    worker.daemon = True
    worker.start()
src_issues = jira_log_copier.get_source_issues()
if src_issues is not None:
    for issue in src_issues:
        queue.put(issue)
queue.join()
print ('Done. Took {}'.format(time() - ts))

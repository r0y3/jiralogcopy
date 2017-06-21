#!/usr/bin/env python3

from settings import CREDENTIALS, PROJECTS, UPDATED_SINCE_HOURS
from jiracopy import JiraLogCopier
from worker import JiraWorker
from queue import Queue
from time import time
import multiprocessing

def main():
    ts = time()
    jira_log_copier = JiraLogCopier(CREDENTIALS, PROJECTS, UPDATED_SINCE_HOURS)
    queue = Queue()
    for x in range(multiprocessing.cpu_count()):
        worker = JiraWorker(queue, jira_log_copier)
        worker.daemon = True
        worker.start()
    frm, to, src_issues = jira_log_copier.get_source_issues()
    if src_issues:
        for issue in src_issues:
            queue.put((frm, to, issue))
    queue.join()
    print ('Done. Took {}'.format(time() - ts))

if __name__ == '__main__':
    main()

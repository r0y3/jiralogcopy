from queue import Queue
from threading import Thread

class JiraWorker(Thread):
    def __init__(self, queue, logger):
        Thread.__init__(self)
        self.queue = queue
        self.logger = logger

    def run(self):
        while True:
            frm, to, issue = self.queue.get()
            for logs in [filter(lambda x: x.author.key == self.logger.credentials['from']['username'], worklogs) for worklogs in [self.logger.source.worklogs(issue)]]:
                logs_list = list(logs)
                if len(logs_list) > 0:
                    self.logger.manage_logs(frm, to, issue, logs_list)
            self.queue.task_done()

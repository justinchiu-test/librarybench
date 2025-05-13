import datetime

class DelayedTaskScheduling:
    def __init__(self):
        # list of tuples: (eta, task)
        self.scheduled = []

    def schedule(self, task, eta):
        # eta: datetime.datetime
        self.scheduled.append((eta, task))

    def get_due_tasks(self, now=None):
        now = now or datetime.datetime.now()
        due = []
        remaining = []
        for eta, task in self.scheduled:
            if eta <= now:
                due.append(task)
            else:
                remaining.append((eta, task))
        self.scheduled = remaining
        return due

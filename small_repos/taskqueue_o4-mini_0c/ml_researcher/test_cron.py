from scheduler.cron import CronScheduler
import time

def test_cron_schedule_and_cancel():
    cron = CronScheduler()
    counter = {'count':0}
    def job():
        counter['count'] += 1
    cron.schedule('job1', job, 0.01)
    time.sleep(0.05)
    cron.cancel('job1')
    cnt = counter['count']
    assert cnt >= 3
    assert 'job1' not in cron.list_tasks()

import pytest
from scheduler import ThreadSafeScheduler

def test_plugin_loading_and_usage():
    scheduler = ThreadSafeScheduler()
    results = []
    def plugin(data):
        results.append(data)
    scheduler.load_plugin('p1', plugin)
    # simulate using plugin in post-hook
    def job(): scheduler.plugins['p1']('ok')
    scheduler.schedule('jobp', job, cron_expr=1)
    scheduler.schedule_one_off('onep', job, run_at=__import__('datetime').datetime.now() + __import__('datetime').timedelta(seconds=1))
    time = __import__('time')
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    # two runs: one recurring, one one-off
    assert results.count('ok') == 2

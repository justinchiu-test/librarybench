from background_dispatcher import Dispatcher

def test_schedule_cron_job():
    dsp = Dispatcher()
    def job():
        pass
    result = dsp.schedule_cron_job("*/5 * * * *", job)
    assert result is True
    assert len(dsp.schedule) == 1
    assert dsp.schedule[0]['cron'] == "*/5 * * * *"
    assert dsp.schedule[0]['func'] is job

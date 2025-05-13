from iot_scheduler.priority import set_job_priority, get_job_priority

def test_priority_setting_and_getting():
    set_job_priority('job1', 10)
    assert get_job_priority('job1') == 10
    assert get_job_priority('unknown') is None

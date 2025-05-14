from pipeline.batch import BatchRunner

def test_run_batch_executes_hooks_and_func():
    br = BatchRunner()
    seq = []
    def start():
        seq.append('start')
    def job():
        seq.append('job')
    def end():
        seq.append('end')
    br.add_job('* * * * *', job, start, end)
    assert not br.health_check()
    br.run_batch()
    assert br.health_check()
    assert seq == ['start', 'job', 'end']

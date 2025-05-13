from scheduler.backends import LocalRunner, KubernetesJobSubmitter, SlurmPlugin

def test_localrunner_submit_cancel_reprioritize():
    br = LocalRunner()
    jid = br.submit('r1', {'a':1})
    assert jid in br.jobs
    assert br.cancel(jid)
    assert br.jobs[jid]['status'] == 'cancelled'
    assert br.reprioritize(jid, 5)
    assert br.jobs[jid]['priority'] == 5

def test_kubernetes_submit_cancel_reprioritize():
    br = KubernetesJobSubmitter()
    jid = br.submit('r2', {'b':2})
    assert jid in br.jobs
    assert br.cancel(jid)
    assert br.jobs[jid]['status'] == 'cancelled'
    assert br.reprioritize(jid, 3)
    assert br.jobs[jid]['priority'] == 3

def test_slurm_submit_cancel_reprioritize():
    br = SlurmPlugin()
    jid = br.submit('r3', {'c':3})
    assert jid in br.jobs
    assert br.cancel(jid)
    assert br.jobs[jid]['status'] == 'cancelled'
    assert br.reprioritize(jid, 1)
    assert br.jobs[jid]['priority'] == 1

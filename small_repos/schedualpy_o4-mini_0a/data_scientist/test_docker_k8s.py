from scheduler import Scheduler, Task

def test_docker_k8s_support():
    def work(): pass
    resources = {'image': 'img', 'cpus': 2, 'gpus': 1, 'memory': '4Gi'}
    sched = Scheduler()
    t = Task('dock', work, resources=resources)
    spec = sched.launch_container(t)
    assert spec == resources
    assert sched.container_launches == [('dock', resources)]

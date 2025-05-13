from scheduler import Scheduler, Task

def test_pre_and_post_hooks():
    order = []
    def pre(task):
        order.append(f"pre-{task.name}")
    def post(task, result):
        order.append(f"post-{task.name}")
    def work():
        order.append("work")
        return None

    sched = Scheduler()
    sched.register_pre_hook(pre)
    sched.register_post_hook(post)
    t = Task('job', work)
    sched.add_task(t)
    sched.run()
    assert order == ['pre-job', 'work', 'post-job']

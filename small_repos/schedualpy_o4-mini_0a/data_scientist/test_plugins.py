from scheduler import Scheduler, Task
from plugins import SerializerPlugin

def test_serializer_plugin():
    def work():
        return 3
    sched = Scheduler()
    plugin = SerializerPlugin(lambda x: x * 2)
    sched.register_plugin(plugin)
    results = []
    def post(task, res):
        results.append(res)
    sched.register_post_hook(post)
    t = Task('p', work)
    sched.add_task(t)
    sched.run()
    assert results == [6]

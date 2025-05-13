from plugin_framework.decorators import parallelize
from plugin_framework.registry import tasks

def test_parallelize_decorator():
    @parallelize
    def my_task():
        return 42
    assert hasattr(my_task, 'parallelizable')
    assert my_task.parallelizable is True
    assert 'my_task' in tasks
    assert tasks['my_task']() == 42

from tasks.task import Task
from tasks.executor import TaskExecutor
from tasks.context import ExecutionContext

def test_register_and_execute_at_runtime():
    ctx = ExecutionContext({'base': 10})
    execu = TaskExecutor(context=ctx)

    # dynamic creation based on base
    def make_task(n):
        def mul(c, base):
            return {'out': base * n}
        return Task(name=f"mul_{n}",
                    func=mul,
                    input_keys=['base'],
                    output_keys=['out'])
    # imagine runtime condition: base=10, create tasks 1..3
    for i in range(1,4):
        execu.register_task(make_task(i))

    # execute them one by one
    results = []
    for i in range(1,4):
        r = execu.execute(f"mul_{i}")
        results.append(r['out'])

    assert results == [10*1, 10*2, 10*3]
    # context's 'out' is last task's output
    assert ctx['out'] == 30

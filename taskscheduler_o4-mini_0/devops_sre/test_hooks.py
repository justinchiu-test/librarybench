from scheduler.hooks import register_lifecycle_hook, run_startup_hooks, run_pre_shutdown_hooks, run_post_shutdown_hooks

def test_hooks_execution():
    state = []
    def s(): state.append('s')
    def pre(): state.append('pre')
    def post(): state.append('post')
    register_lifecycle_hook('startup', s)
    register_lifecycle_hook('pre_shutdown', pre)
    register_lifecycle_hook('post_shutdown', post)
    run_startup_hooks()
    run_pre_shutdown_hooks()
    run_post_shutdown_hooks()
    assert state == ['s', 'pre', 'post']

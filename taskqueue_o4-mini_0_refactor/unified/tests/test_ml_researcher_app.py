from ml_researcher.scheduler.app import SchedulerApp

def test_app_components():
    app = SchedulerApp()
    app.reload_config({'foo': 'bar'})
    assert app.config.get('foo') == 'bar'
    dot = app.visualize_dag(['p','q'], [('p','q')])
    assert '"p" -> "q"' in dot

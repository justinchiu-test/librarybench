import pytest
from plugin_framework.decorators import export_workflow
from plugin_framework.registry import workflow_steps
from plugin_framework.workflow_exporter import export_workflow

def test_export_workflow_md():
    workflow_steps.clear()
    @export_workflow
    def step_one():
        "First step"
        pass
    @export_workflow
    def step_two():
        "Second step"
        pass
    md = export_workflow(format='md')
    assert '## step_one' in md
    assert 'First step' in md
    assert '## step_two' in md

def test_export_workflow_html():
    workflow_steps.clear()
    @export_workflow
    def html_step():
        "HTML step"
        pass
    html = export_workflow(format='html')
    assert '<h2>html_step</h2>' in html
    assert '<p>HTML step</p>' in html

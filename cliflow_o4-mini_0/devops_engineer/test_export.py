import pytest
from cli_framework.export import Flow, export_docs

def test_export_md():
    flow = Flow("TestFlow")
    flow.add_step("Step1", "Do something")
    md = export_docs(flow, format='md')
    assert "# Flow: TestFlow" in md
    assert "## Step: Step1" in md

def test_export_html():
    flow = Flow("TestFlow")
    flow.add_step("Step1", "Do something")
    html = export_docs(flow, format='html')
    assert "<h1>Flow: TestFlow</h1>" in html
    assert "<h2>Step: Step1</h2>" in html

def test_export_invalid():
    flow = Flow("Test")
    with pytest.raises(ValueError):
        export_docs(flow, format='txt')

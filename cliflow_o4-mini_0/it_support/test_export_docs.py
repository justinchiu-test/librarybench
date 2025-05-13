import pytest
from onboarding.export_docs import export_docs

def test_export_markdown():
    steps = ["Install OS", "Install software"]
    md = export_docs(steps, format='markdown')
    assert "# Onboarding Workflow" in md
    assert "1. Install OS" in md

def test_export_html():
    steps = ["Step1", "Step2"]
    html = export_docs(steps, format='html')
    assert "<ol><li>Step1</li><li>Step2</li></ol>" in html

def test_export_invalid():
    with pytest.raises(ValueError):
        export_docs([], format='txt')

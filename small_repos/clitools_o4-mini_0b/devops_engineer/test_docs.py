from devops_cli.docs import generate_docs

def test_generate_docs():
    spec = {"cmd": "does something"}
    out = generate_docs(spec, formats=["md", "rst", "html", "man"])
    assert "## cmd" in out["md"]
    assert "cmd" in out["rst"]
    assert "<li><strong>cmd</strong>" in out["html"]
    assert ".TH CLI 1" in out["man"]

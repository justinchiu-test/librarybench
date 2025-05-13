from adapters.security_analyst.cli_framework.docs import generate_docs

def test_docs():
    cmds = {"init": "Initialize", "run": "Run tool"}
    doc = generate_docs(cmds)
    assert "SECURITY" in doc
    assert "init\tInitialize" in doc
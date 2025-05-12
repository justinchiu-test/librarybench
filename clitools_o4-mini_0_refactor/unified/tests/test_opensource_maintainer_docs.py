from opensource_maintainer.osscli.docs import generate_docs
def test_generate_docs():
    cmds = ["a", "b"]
    docs = generate_docs(cmds)
    assert "md" in docs and "- a" in docs["md"]
    assert "html" in docs and "<p>a</p>" in docs["html"]
    assert "rst" in docs and "- b" in docs["rst"]
    assert "man" in docs and "COMMANDS" in docs["man"]

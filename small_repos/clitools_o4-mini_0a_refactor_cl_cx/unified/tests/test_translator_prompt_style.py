from translator.prompt_style import PromptStyle

def test_style_wraps_text():
    text = "Hello"
    styled = PromptStyle.style(text, 'red')
    assert styled.startswith('\033[91m')
    assert styled.endswith('\033[0m')
    assert "Hello" in styled

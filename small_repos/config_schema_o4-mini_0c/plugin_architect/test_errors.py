from config_manager.errors import report_error

def test_report_error_without_suggestion():
    msg = report_error("file.yaml", 10, "sec", "key", "int", "str")
    assert "file.yaml:10:" in msg
    assert "expected int, got str" in msg

def test_report_error_with_suggestion():
    msg = report_error("file.yaml", 1, "s", "k", "float", "int", suggestion="use float")
    assert "Suggestion: use float" in msg

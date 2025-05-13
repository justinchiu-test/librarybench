import pytest
from validation import Schema, Field, Validator
from validation.plugins import corporate_email_plugin

def test_corporate_plugin_pass():
    fields = [Field("email", str, required=True)]
    schema = Schema(fields)
    plugin = corporate_email_plugin("biz.com")
    v = Validator(schema, plugins=[plugin])
    data = {"email": "user@biz.com"}
    cleaned = v.validate(data)
    assert cleaned["email"] == "user@biz.com"

def test_corporate_plugin_fail():
    fields = [Field("email", str, required=True)]
    schema = Schema(fields)
    plugin = corporate_email_plugin("biz.com")
    v = Validator(schema, plugins=[plugin])
    with pytest.raises(Exception) as e:
        v.validate({"email": "user@other.com"})
    assert "Email must end with @biz.com" in str(e.value)

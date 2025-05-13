import pytest
import yaml
import asyncio
from form_validator import FormValidator, PluginInterface

@pytest.mark.anyio
async def test_enum_constraints(default_username_check):
    fv = FormValidator(username_check_func=default_username_check)
    data = {
        'username': 'user1', 'password': 'password123', 'age': 30,
        'gender': 'invalid', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'individual'
    }
    res = await fv.validate(data)
    assert 'gender' in res['errors']
    assert 'Value must be one of' in res['errors']['gender'][0]

@pytest.mark.anyio
async def test_conditional_validation(default_username_check):
    fv = FormValidator(username_check_func=default_username_check)
    data = {
        'username': 'user1', 'password': 'password123', 'age': 30,
        'gender': 'male', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'business'
    }
    res = await fv.validate(data)
    assert 'company_name' in res['errors']
    assert 'required for business' in res['errors']['company_name'][0]

@pytest.mark.anyio
async def test_default_values(default_username_check):
    fv = FormValidator(username_check_func=default_username_check, browser_locale='fr-FR')
    data = {
        'username': 'user1', 'password': 'password123', 'age': 30,
        'gender': 'male', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'individual', 'country': '', 'language': ''
    }
    res = await fv.validate(data)
    assert res['data']['country'] == 'US'
    assert res['data']['language'] == 'fr-FR'

@pytest.mark.anyio
async def test_range_checks(default_username_check):
    fv = FormValidator(username_check_func=default_username_check)
    data = {
        'username': 'user1', 'password': 'short', 'age': 10,
        'gender': 'male', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'individual'
    }
    res = await fv.validate(data)
    assert 'password' in res['errors']
    assert 'Length must be >=' in res['errors']['password'][0]
    assert 'age' in res['errors']
    assert 'Value must be >=' in res['errors']['age'][0]

@pytest.mark.anyio
async def test_async_username_uniqueness(default_username_check):
    fv = FormValidator(username_check_func=default_username_check)
    data = {
        'username': 'taken', 'password': 'password123', 'age': 30,
        'gender': 'male', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'individual'
    }
    res = await fv.validate(data)
    assert 'username' in res['errors']
    data['username'] = 'free'
    res = await fv.validate(data)
    assert 'username' not in res['errors']

@pytest.mark.anyio
async def test_optional_fields(default_username_check):
    fv = FormValidator(username_check_func=default_username_check)
    data = {
        'username': 'user1', 'password': 'password123', 'age': 30,
        'gender': 'male', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'individual'
    }
    res = await fv.validate(data)
    assert 'profile_picture' not in res['errors']
    assert 'bio' not in res['errors']

@pytest.mark.anyio
async def test_strict_mode(default_username_check):
    fv = FormValidator(username_check_func=default_username_check, strict_mode=True)
    data = {
        'username': 'user1', 'password': 'password123', 'age': 30,
        'gender': 'male', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'individual', 'unknown_field': 'value'
    }
    res = await fv.validate(data)
    assert 'unknown_field' in res['errors']
    assert 'Unknown field' in res['errors']['unknown_field'][0]

@pytest.mark.anyio
async def test_lenient_mode(default_username_check):
    fv = FormValidator(username_check_func=default_username_check, strict_mode=False)
    data = {
        'username': 'user1', 'password': 'password123', 'age': 30,
        'gender': 'male', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'individual', 'unknown_field': 'value'
    }
    res = await fv.validate(data)
    assert 'unknown_field' not in res['errors']

@pytest.mark.anyio
async def test_plugin_system(default_username_check):
    fv = FormValidator(username_check_func=default_username_check)
    class CustomPlugin(PluginInterface):
        def validate(self, data, errors):
            if data.get("bio") == "":
                errors.setdefault("bio", []).append("Bio cannot be empty string")
    fv.register_plugin(CustomPlugin())
    data = {
        'username': 'user1', 'password': 'password123', 'age': 30,
        'gender': 'male', 'plan_type': 'basic', 'newsletter_opt_in': True,
        'user_type': 'individual', 'bio': ''
    }
    res = await fv.validate(data)
    assert 'bio' in res['errors']
    assert 'Bio cannot be empty string' in res['errors']['bio'][0]

def test_schema_import_export():
    fv = FormValidator()
    yaml_str = fv.export_schema()
    loaded = yaml.safe_load(yaml_str)
    loaded['plan_type']['enum'] = ['silver', 'gold']
    new_yaml = yaml.safe_dump(loaded)
    fv.import_schema(new_yaml)
    data = {
        'username': 'user', 'password': 'password123', 'age': 30,
        'gender': 'male', 'plan_type': 'free', 'newsletter_opt_in': True,
        'user_type': 'individual'
    }
    res = asyncio.get_event_loop().run_until_complete(fv.validate(data))
    assert 'plan_type' in res['errors']
    assert 'Value must be one of' in res['errors']['plan_type'][0]

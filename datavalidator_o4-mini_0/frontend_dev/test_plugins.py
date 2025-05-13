import pytest
import asyncio
from plugins import CreditCardPlugin, AddressAutocompletePlugin, ReCaptchaPlugin
from form_validator import FormValidator

def test_credit_card_plugin_valid():
    fv = FormValidator()
    plugin = CreditCardPlugin()
    fv.register_plugin(plugin)
    data = {
        'username': 'u', 'password': 'password1', 'age': 20,
        'gender': 'male', 'plan_type': 'free', 'newsletter_opt_in': True,
        'user_type': 'individual', 'cc_number': '1234567812345678'
    }
    # Direct async call
    res = asyncio.get_event_loop().run_until_complete(fv.validate(data))
    assert 'cc_number' not in res['errors']

def test_credit_card_plugin_invalid():
    fv = FormValidator()
    plugin = CreditCardPlugin()
    fv.register_plugin(plugin)
    data = {
        'username': 'u', 'password': 'password1', 'age': 20,
        'gender': 'male', 'plan_type': 'free', 'newsletter_opt_in': True,
        'user_type': 'individual', 'cc_number': 'invalid'
    }
    res = asyncio.get_event_loop().run_until_complete(fv.validate(data))
    assert 'cc_number' in res['errors']

def test_address_plugin():
    fv = FormValidator()
    plugin = AddressAutocompletePlugin()
    fv.register_plugin(plugin)
    data = {
        'username': 'u', 'password': 'password1', 'age': 20,
        'gender': 'male', 'plan_type': 'free', 'newsletter_opt_in': True,
        'user_type': 'individual', 'address': '123 Main Ave'
    }
    res = asyncio.get_event_loop().run_until_complete(fv.validate(data))
    assert 'address' in res['errors']

def test_recaptcha_plugin():
    fv = FormValidator()
    plugin = ReCaptchaPlugin()
    fv.register_plugin(plugin)
    data = {
        'username': 'u', 'password': 'password1', 'age': 20,
        'gender': 'male', 'plan_type': 'free', 'newsletter_opt_in': True,
        'user_type': 'individual', 'recaptcha_token': 'invalid'
    }
    res = asyncio.get_event_loop().run_until_complete(fv.validate(data))
    assert 'recaptcha_token' in res['errors']

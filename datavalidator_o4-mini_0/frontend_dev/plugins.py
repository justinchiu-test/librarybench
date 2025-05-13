from form_validator import PluginInterface

class CreditCardPlugin(PluginInterface):
    def validate(self, data, errors):
        cc = data.get("cc_number")
        if cc:
            import re
            if not re.fullmatch(r"\d{16}", str(cc)):
                errors.setdefault("cc_number", []).append("Invalid credit card number")

class AddressAutocompletePlugin(PluginInterface):
    def validate(self, data, errors):
        addr = data.get("address")
        if addr and not addr.endswith("Street"):
            errors.setdefault("address", []).append("Address must end with 'Street'")

class ReCaptchaPlugin(PluginInterface):
    def validate(self, data, errors):
        token = data.get("recaptcha_token")
        if not token or token != "valid":
            errors.setdefault("recaptcha_token", []).append("Invalid reCAPTCHA")

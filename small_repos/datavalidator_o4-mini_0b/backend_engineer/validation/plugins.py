from .core import FieldError

def corporate_email_plugin(domain):
    def plugin(data, errors):
        email = data.get("email")
        if email and not email.endswith("@" + domain):
            msg = f"Email must end with @{domain}"
            errors.append(FieldError("email", msg))
        return
    return plugin

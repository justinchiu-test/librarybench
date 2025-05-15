import re
import ipaddress

def validate_input(input_type, value):
    if input_type == "incident_id":
        pattern = re.compile(r"^INC-\d{4}$")
        if pattern.match(value):
            return True, None
        return False, "Invalid incident ID format"
    elif input_type == "ip":
        try:
            ipaddress.ip_address(value)
            return True, None
        except ValueError:
            return False, "Invalid IP address"
    elif input_type == "general":
        # Allow alphanumerics and basic punctuation
        if re.match(r"^[\w\s\.\,\-\_\(\)]+$", value):
            return True, None
        return False, "Unauthorized characters detected"
    else:
        return False, "Unknown input type"

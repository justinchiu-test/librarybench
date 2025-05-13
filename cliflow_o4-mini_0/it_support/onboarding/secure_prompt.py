import getpass

def secure_prompt(prompt):
    try:
        value = getpass.getpass(prompt)
        return value
    finally:
        # Clear local variable
        value = None

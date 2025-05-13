import getpass

def secure_input(prompt):
    val = getpass.getpass(prompt)
    # Attempt to wipe prompt; Python strings are immutable
    return val

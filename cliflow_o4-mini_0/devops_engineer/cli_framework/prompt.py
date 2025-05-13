import getpass

def prompt_interactive(prompt, choices=None, type=str, default=None):
    while True:
        if choices:
            display = "/".join(str(c) for c in choices)
            val = input(f"{prompt} [{display}]: ")
            ifval = val or default
            if ifval in choices:
                return type(ifval)
        else:
            val = input(f"{prompt}: ")
            val = val or default
            try:
                return type(val)
            except Exception:
                print(f"Invalid {type.__name__}, try again")

def secure_prompt(prompt):
    val = getpass.getpass(prompt)
    result = val
    val = None
    return result

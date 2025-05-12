"""
Register CLI subcommands for backend developers.
"""
def migrate():
    pass

def seed():
    pass

def status():
    pass

def register_subcommands():
    return {
        'migrate': migrate,
        'seed': seed,
        'status': status,
    }
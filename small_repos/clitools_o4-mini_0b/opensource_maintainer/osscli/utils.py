import datetime
import random
import string

def compute_default(key):
    if key == "build_dir":
        return "build"
    elif key == "docs_dir":
        return datetime.datetime.now().strftime("docs_%Y%m%d")
    elif key == "token":
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    else:
        return None

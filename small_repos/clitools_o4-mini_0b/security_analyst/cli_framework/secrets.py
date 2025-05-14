import subprocess
import os

def fetch_secret(uri):
    if uri.startswith("gpg://"):
        path = uri[len("gpg://"):]
        if not os.path.exists(path):
            raise FileNotFoundError
        with open(path) as f:
            return f.read()
    elif uri.startswith("kms://") or uri.startswith("vault://"):
        raise NotImplementedError
    else:
        raise ValueError("Unsupported URI")

"""
Secret fetching for DevOps Engineer CLI.
"""
def fetch_secret_aws(secret_id):
    return f"secret_for_{secret_id}"

def fetch_secret_vault(path):
    return f"vault_secret_for_{path}"
from adapters.devops_engineer.devops_cli.secrets import fetch_secret_aws, fetch_secret_vault

def test_fetch_secret_aws():
    assert fetch_secret_aws("id") == "secret_for_id"

def test_fetch_secret_vault():
    assert fetch_secret_vault("path") == "vault_secret_for_path"
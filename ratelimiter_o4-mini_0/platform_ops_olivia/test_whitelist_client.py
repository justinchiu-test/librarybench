from ratelimiter.whitelist import whitelist_client, is_client_whitelisted

def test_whitelist_client_adds_and_checks():
    client = 'serviceA'
    assert not is_client_whitelisted(client)
    whitelist_client(client)
    assert is_client_whitelisted(client)

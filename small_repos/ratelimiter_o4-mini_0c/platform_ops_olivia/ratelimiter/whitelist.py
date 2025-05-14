_whitelist = set()

def whitelist_client(client_id):
    _whitelist.add(client_id)

def is_client_whitelisted(client_id):
    return client_id in _whitelist

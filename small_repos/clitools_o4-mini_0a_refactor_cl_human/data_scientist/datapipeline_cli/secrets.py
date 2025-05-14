import os

def manage_secrets(keys, store=None):
    store = store or os.environ.get('SECRET_STORE', 'env')
    secrets = {}
    if store == 'env':
        for key in keys:
            if key not in os.environ:
                raise KeyError(f'Missing secret: {key}')
            secrets[key] = os.environ[key]
    else:
        raise ValueError('Unsupported secret store')
    return secrets

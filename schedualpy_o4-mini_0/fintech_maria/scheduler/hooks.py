import threading

_pre_hooks = []
_post_hooks = []

def register_pre_post_hooks(pre_hook, post_hook):
    """
    Register pre and post hooks for transactional context.
    """
    _pre_hooks.append(pre_hook)
    _post_hooks.append(post_hook)

def apply_hooks(func):
    """
    Decorator to wrap a task function with pre and post hooks.
    """
    def wrapper(*args, **kwargs):
        for pre in _pre_hooks:
            pre()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            for post in _post_hooks:
                post(exception=e)
            raise
        else:
            for post in _post_hooks:
                post(exception=None)
            return result
    return wrapper

# Simulated transaction functions
class DBTransactionSimulator:
    def __init__(self):
        self.active = False
    def begin(self):
        self.active = True
    def commit(self):
        if self.active:
            self.active = False
    def rollback(self):
        if self.active:
            self.active = False

# Default hooks using simulator
_db_tx = DBTransactionSimulator()
def _default_pre():
    _db_tx.begin()
def _default_post(exception):
    if exception:
        _db_tx.rollback()
    else:
        _db_tx.commit()

# Register default hooks
register_pre_post_hooks(_default_pre, _default_post)

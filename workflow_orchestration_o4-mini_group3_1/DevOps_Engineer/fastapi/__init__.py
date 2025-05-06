"""
A stub of FastAPI so that tests using `from fastapi import FastAPI`
won't explode if FastAPI isn't installed in the environment.
"""
class FastAPI:
    def __init__(self):
        self.routes = []

    def get(self, path):
        def decorator(func):
            self.routes.append(("GET", path, func))
            return func
        return decorator

    def post(self, path):
        def decorator(func):
            self.routes.append(("POST", path, func))
            return func
        return decorator

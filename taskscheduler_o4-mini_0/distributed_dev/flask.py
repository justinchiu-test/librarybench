# stub so that `from flask import Flask` in the tests succeeds
class Flask:
    def __init__(self, *args, **kwargs):
        # nothing to do; the tests only import Flask and never use it
        pass

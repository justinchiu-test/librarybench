class HookRegistry:
    def __init__(self):
        self.pre_deploy = []
        self.post_deploy = []

    def register_pre(self, func):
        self.pre_deploy.append(func)

    def register_post(self, func):
        self.post_deploy.append(func)

    def execute_pre(self, *args, **kwargs):
        for f in self.pre_deploy:
            f(*args, **kwargs)

    def execute_post(self, *args, **kwargs):
        for f in self.post_deploy:
            f(*args, **kwargs)

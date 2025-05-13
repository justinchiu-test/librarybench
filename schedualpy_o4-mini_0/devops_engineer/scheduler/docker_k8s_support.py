class DockerK8sSupport:
    def __init__(self, values=None):
        self.values = values or {}

    def deploy_docker(self, image_name):
        if not image_name:
            raise ValueError("Image name required")
        # dummy deploy
        return True

    def deploy_k8s(self, chart_name, values=None):
        if not chart_name:
            raise ValueError("Chart name required")
        # dummy deploy
        return True

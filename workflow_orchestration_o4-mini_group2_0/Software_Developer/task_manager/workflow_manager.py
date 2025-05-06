class WorkflowManager:
    def __init__(self):
        self.workflows = []

    def register(self, workflow):
        existing = [w.version for w in self.workflows if w.name == workflow.name]
        next_v = max(existing) + 1 if existing else 1
        workflow.version = next_v
        self.workflows.append(workflow)

    def get(self, name, version):
        for w in self.workflows:
            if w.name == name and w.version == version:
                return w
        return None

workflow_manager = WorkflowManager()

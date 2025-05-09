from .workflow import Workflow

class WorkflowManager:
    def __init__(self):
        # flat list of all registered workflows
        self.workflows = []

    def register(self, workflow: Workflow):
        """
        Assign the next version for this workflow.name and store it.
        """
        # find existing versions for same name
        existing = [w.version for w in self.workflows if w.name == workflow.name]
        next_version = max(existing) + 1 if existing else 1
        workflow.version = next_version
        self.workflows.append(workflow)

    def get(self, name: str, version: int):
        """
        Lookup a registered workflow by name & version, or return None.
        """
        for w in self.workflows:
            if w.name == name and w.version == version:
                return w
        return None

# module‐level manager instance, for use by the API and tests
workflow_manager = WorkflowManager()

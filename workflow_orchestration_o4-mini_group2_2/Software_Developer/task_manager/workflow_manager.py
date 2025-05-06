from .workflow import Workflow
from utils import next_version

class WorkflowManager:
    def __init__(self):
        # flat list of all registered workflows
        self.workflows = []

    def register(self, workflow: Workflow):
        """
        Assign the next version for this workflow.name and store it.
        """
        existing = [w.version for w in self.workflows if w.name == workflow.name]
        workflow.version = next_version(existing)
        self.workflows.append(workflow)

    def get(self, name: str, version: int):
        """
        Lookup a registered workflow by name & version, or return None.
        """
        for w in self.workflows:
            if w.name == name and w.version == version:
                return w
        return None

    def get_latest(self, name: str):
        """
        Return the latest version of a workflow by name, or None.
        """
        versions = [w for w in self.workflows if w.name == name]
        return versions[-1] if versions else None

# module‐level manager instance, for use by the API and tests
workflow_manager = WorkflowManager()

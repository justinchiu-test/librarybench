import sys
import os

# Add the o4-mini_iterative package root to PYTHONPATH so that
# `import project_manager.task` will find the code under workflow_orchestration_ProjectManager_o4-mini_iterative/
root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "workflow_orchestration_ProjectManager_o4-mini_iterative"))
if root not in sys.path:
    sys.path.insert(0, root)

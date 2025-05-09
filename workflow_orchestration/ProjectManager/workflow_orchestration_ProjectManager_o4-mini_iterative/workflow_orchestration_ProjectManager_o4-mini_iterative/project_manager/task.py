@@
+from enum import Enum
+
+class TaskState(Enum):
+    PENDING = "PENDING"
+    READY   = "READY"
+    RUNNING = "RUNNING"
+    SUCCESS = "SUCCESS"
+    FAILED  = "FAILED"
 
 import threading
 import time
 import traceback
@@
 class Task:
     """
     A single unit of work.  Tasks can depend on other Tasks, will
     automatically wait until their dependencies have succeeded, and then
@@
     def __init__(self, name, func, inputs=None, outputs=None,
                  retries=0, backoff=0, timeout=None):
         self.name       = name
         self.func       = func
@@
         self.state      = TaskState.PENDING
         self.result     = None
         self.exception  = None
         self._lock      = threading.Lock()
         self._cond      = threading.Condition(self._lock)
@@
     def set_ready(self):
         with self._lock:
-            self.state = "READY"
+            self.state = TaskState.READY
             self._cond.notify_all()
@@
     def run(self):
         with self._lock:
-            self.state = "RUNNING"
+            self.state = TaskState.RUNNING
         # ... rest of existing run logic stays unchanged ...

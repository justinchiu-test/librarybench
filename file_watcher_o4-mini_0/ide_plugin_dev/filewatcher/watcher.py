--- a/filewatcher/watcher.py
+++ b/filewatcher/watcher.py
@@ async def _detect_changes(self, old, new):
-        # modified
-        for path in new.keys() & old.keys():
-            if new[path]['mtime'] != old[path]['mtime']:
-                diff = None
-                old_c = old[path]['content']
-                new_c = new[path]['content']
-                if old_c is not None and new_c is not None:
-                    diff = ''.join(difflib.unified_diff(
-                        old_c.splitlines(keepends=True),
-                        new_c.splitlines(keepends=True),
-                        fromfile=path, tofile=path
-                    ))
-                ev = Event('modified', path, diff=diff)
-                await self._emit(ev)
+        # modified (either mtime changed or content changed)
+        for path in new.keys() & old.keys():
+            old_entry = old[path]
+            new_entry = new[path]
+            old_mtime = old_entry['mtime']
+            new_mtime = new_entry['mtime']
+            old_c = old_entry['content']
+            new_c = new_entry['content']
+            changed = False
+            # if mtime differs, or content differs when both are readable
+            if new_mtime != old_mtime:
+                changed = True
+            elif old_c is not None and new_c is not None and new_c != old_c:
+                changed = True
+            if changed:
+                diff = None
+                if old_c is not None and new_c is not None:
+                    diff = ''.join(difflib.unified_diff(
+                        old_c.splitlines(keepends=True),
+                        new_c.splitlines(keepends=True),
+                        fromfile=path, tofile=path
+                    ))
+                ev = Event('modified', path, diff=diff)
+                await self._emit(ev)

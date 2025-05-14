--- a/filewatcher/webhook.py
+++ b/filewatcher/webhook.py
@@ class WebhookServer:
-    async def broadcast(self, event):
-        data = json.dumps(event.to_dict())
-        msg = f"data: {data}\n\n"
-        for client in list(self._clients):
-            try:
-                await client.write(msg.encode('utf-8'))
-            except Exception:
-                self.logger.warning("Removing client due to error")
-                self._clients.remove(client)
+    async def broadcast(self, event):
+        # Send one SSE message and then close so client.release() completes
+        data = json.dumps(event.to_dict())
+        msg = f"data: {data}\n\n".encode('utf-8')
+        for client in list(self._clients):
+            try:
+                # write the event
+                await client.write(msg)
+                # signal EOF so the client sees end-of-stream
+                await client.write_eof()
+            except Exception:
+                self.logger.warning("Removing client due to error")
+            finally:
+                # remove client so we don't try to write again
+                if client in self._clients:
+                    self._clients.remove(client)

# The Task

I am an IDE plugin developer building a live file explorer and refactoring tool. I want to listen for file operations in the user’s project workspace and update my in-editor tree, diff panes, and refactoring previews seamlessly. This code repository is my low-overhead, cross-platform file-watching engine that plugs into my async plugin host.

# The Requirements

* `LoggingSupport` : Log watcher lifecycle events at adjustable levels for debugging issues in user workspaces.
* `WebhookIntegration` : Expose a local webhook receiver so the plugin host can subscribe to file event streams.
* `DynamicFilterRules` : Let the user add/exclude directories or file types (e.g. `node_modules`, `*.tmp`) at runtime through the plugin settings dialog.
* `HighLevelEventDetection` : Receive structured create, modify, delete, and move events to update the tree view and trigger refactor analyses.
* `CrossPlatformConsistency` : Guarantee identical hook behavior in VS Code on Windows, macOS, and Linux distributions.
* `CLIInterface` : Provide a dev CLI to simulate file events during plugin development.
* `AsyncIOAPI` : Fit naturally into the asyncio-based extension host for non-blocking integration.
* `RecursiveDirectoryWatch` : Watch entire project roots recursively, respecting include/exclude rules per module.
* `ResilientErrorHandling` : Automatically retry on ephemeral file locks or permission failures, with callbacks to display errors in the IDE status bar.
* `InlineDiffs` : Generate inline diffs for text file modifications so the plugin can render live diff previews in the editor pane.


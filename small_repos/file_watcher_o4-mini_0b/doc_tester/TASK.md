# The Task

I am a documentation QA specialist tasked with keeping our Markdown documentation and example notebooks pristine. I want to catch every inline typo, header change, or code snippet update in real time so I can auto-generate review tickets and notify writers immediately. This code repository empowers me with a flexible watcher that can diff every textual change and ship it to my review bots.

# The Requirements

* `LoggingSupport` : Fine-tune log verbosity for debug vs. info in my test harness, and route logs to both console and a rotating file.
* `WebhookIntegration` : Send change events to GitHub Actions or our custom review bot endpoints via HTTP POST.
* `DynamicFilterRules` : Add new file patterns (e.g., `*.md`, `*.ipynb`) or exclude vendor docs on the fly without restarting my watchers.
* `HighLevelEventDetection` : Distinguish create/modify/delete/move so I don’t run diffs on newly added images or binary assets.
* `CrossPlatformConsistency` : Ensure my QA scripts run the same on Windows authors’ machines, my Linux CI runner, and my macOS lab.
* `CLIInterface` : Launch quick local watchers via a simple CLI when I’m iterating on new test cases.
* `AsyncIOAPI` : Integrate into our asyncio-based test runner to keep the main event loop non-blocking.
* `RecursiveDirectoryWatch` : Track nested docs folders under various language or module directories.
* `ResilientErrorHandling` : Handle transient file-system locks or permission hiccups on Windows when multiple editors hit the same files.
* `InlineDiffs` : Embed precise line-by-line diffs for every Markdown change in the webhook payload so upstream writers see exactly what to fix.


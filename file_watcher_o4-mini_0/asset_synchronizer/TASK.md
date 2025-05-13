# The Task

I am an Asset Synchronization Specialist ensuring that multimedia content is mirrored across cloud storage and CDN nodes. I want to detect new or updated assets in my local directory, batch changes, and push only the deltas through our upload API. This code repository streamlines content synchronization with flexible filtering and robust event delivery.

# The Requirements

* `snapshotDiff`       : Create initial full snapshots then compute incremental diffs to identify added, modified, or removed media files.
* `fileHashComparison` : Compare SHA-1 hashes to avoid re-uploading unchanged large files.
* `dynamicFilterRules` : Dynamically update include/exclude patterns for file types (.jpg, .mp4, .svg) as requirements evolve.
* `loggingSupport`     : Enable fine-grained transfer logs, select human-readable or machine-friendly formats for post-sync reporting.
* `configFileSupport`  : Store sync parameters in external JSON/TOML for easy updates across different content projects.
* `gitignoreParsing`   : Automatically skip files listed in `.gitignore` (e.g., source PSDs or .tmp edits).
* `restfulAPI`         : Trigger sync jobs, query status, and report errors via a standardized REST API.
* `eventBatching`      : Group file events into bulk upload batches to optimize network usage and reduce API calls.
* `cliInterface`       : Offer a command-line tool for quick one-off syncs and live progress feedback.
* `hiddenFileFilter`   : Optionally exclude hidden files so only intended assets are propagated.

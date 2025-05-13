# The Task

I am a machine learning researcher preparing large datasets for feature engineering and model training. I want to ensure data quality, apply grouping and batching for vectorized computations, sort records for sequence models, and cache intermediate outputs. This code repository helps me validate and enforce schema, version my data flows, and optimize iterative workflows.

# The Requirements

* `DataValidation` : Validate input records against user-defined rules or JSON Schema, dropping or quarantining invalid entries.
* `SchemaEnforcement` : Enforce an evolving schema on incoming data to detect and block breaking changes early.
* `BuiltInGroup` : Group records by one or more fields, emitting lists or aggregate statistics for feature calculations.
* `BuiltInBatch` : Batch incoming records into fixed-size or time-based groups for efficient downstream processing.
* `BuiltInSort` : Sort records by arbitrary keys to prepare inputs for sequence or ranking algorithms.
* `Versioning` : Track pipeline stage versions and data snapshots for reproducible experiments and rollbacks.
* `CachingStage` : Cache intermediate results in memory or on disk to speed up iterative feature extraction loops.

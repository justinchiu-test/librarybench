# The Task

I am a data engineer responsible for building and maintaining pipelines that bring in data from many sources. I want to be able to evolve my validation logic as schemas change, catch errors early with precise codes, and run both single-record checks during development and bulk validations in production. This code repository gives me a comprehensive toolkit to define, version, and validate my schemas and data with full observability.

# The Requirements

* `version_schemas`         : Manage schema versions and apply migrations over time (VersionedSchemas)  
* `assign_error_codes`      : Return consistent, machine-readable error codes for every validation rule (ErrorCodeSupport)  
* `extend_schema`           : Inherit from base schemas or compose multiple schemas to avoid duplication (SchemaInheritance)  
* `report_performance`      : Hook into validation to measure timing, throughput, and emit performance metrics (PerformanceMetrics)  
* `validate_batch`          : Validate lists of records in bulk and produce summary reports (BatchValidationInterface)  
* `set_default_values`      : Automatically fill in missing fields with sensible defaults (DefaultValues)  
* `validate_single`         : Validate a single record and get detailed, per-field feedback (SingleItemValidation)  
* `conditional_validation`  : Apply field‐level rules only when other fields meet specified conditions (ConditionalValidation)  
* `length_constraints`      : Enforce minimum and maximum lengths on strings, lists, and dictionaries (LengthConstraints)  
* `optional_fields`         : Declare which fields are optional or required, with custom fallback logic (OptionalFields)  

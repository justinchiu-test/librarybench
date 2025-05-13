# The Task

I am an API architect designing a public-facing REST and GraphQL interface. I want to define strict request and response schemas that evolve gracefully, enforce complex conditional rules, and return standardized error codes so clients can automate error handling. This code repository provides me with version control for schemas, rule inheritance for modularity, and hooks for both single‐call and bulk request validations.

# The Requirements

* `version_schemas`         : Track schema changes and run migrations for backward and forward compatibility (VersionedSchemas)  
* `assign_error_codes`      : Attach machine‐readable codes to every validation failure for client automation (ErrorCodeSupport)  
* `extend_schema`           : Reuse common API shapes and override fields in specialized endpoints (SchemaInheritance)  
* `report_performance`      : Capture per‐request timing and throughput metrics for SLA monitoring (PerformanceMetrics)  
* `validate_batch`          : Support batch‐endpoints that accept arrays of objects and return an aggregate report (BatchValidationInterface)  
* `set_default_values`      : Supply default parameters when clients omit optional query or body fields (DefaultValues)  
* `validate_single`         : Run field‐by‐field checks on individual requests to power detailed error responses (SingleItemValidation)  
* `conditional_validation`  : Enforce inter‐field rules such as “if `type=advanced` then `config` must be present” (ConditionalValidation)  
* `length_constraints`      : Limit string lengths in path and payload to prevent abuse and ensure consistency (LengthConstraints)  
* `optional_fields`         : Mark headers or JSON fields as optional or required with custom error levels (OptionalFields)  

# The Task

I am a QA analyst tasked with verifying dataset integrity before every release. I need fine‐grained control over rules, the ability to simulate downstream defaults, and clear outcome codes for dashboards. I also want to test corner cases one record at a time and run nightly full‐set validations while tracking performance. This code repository covers all those needs in one package.

# The Requirements

* `version_schemas`         : Apply the correct schema version on each dataset build (VersionedSchemas)  
* `assign_error_codes`      : Map each rule violation to a code for dashboard filtering (ErrorCodeSupport)  
* `extend_schema`           : Combine common test suites and override rules for special cases (SchemaInheritance)  
* `report_performance`      : Hook validation into CI to measure runtime regression (PerformanceMetrics)  
* `validate_batch`          : Execute nightly bulk validations and generate summary reports (BatchValidationInterface)  
* `set_default_values`      : Simulate default‐value behavior to catch missing‐field regressions (DefaultValues)  
* `validate_single`         : Hand‐test individual records and inspect precise feedback (SingleItemValidation)  
* `conditional_validation`  : Turn on conditional checks only for certain QA scenarios (ConditionalValidation)  
* `length_constraints`      : Verify limits on descriptions, comments, and field lists (LengthConstraints)  
* `optional_fields`         : Toggle optional fields in test plans to cover both strict and lenient modes (OptionalFields)  

# The Task

I am a machine learning researcher preparing training data pipelines. I need to ensure that each record fits evolving schema versions, apply default imputations automatically, and flag complex anomalies with clear error codes. I also want to batch‐validate new datasets at scale, track speed, and run one‐off checks during experiments. This code repository equips me with flexible, versioned schemas and rich validation capabilities.

# The Requirements

* `version_schemas`         : Version and migrate feature schemas as experiments evolve (VersionedSchemas)  
* `assign_error_codes`      : Label anomalies with codes like `MISSING_FEATURE` or `OUTLIER_DETECTED` (ErrorCodeSupport)  
* `extend_schema`           : Inherit from base feature sets and override experimental fields (SchemaInheritance)  
* `report_performance`      : Log validation throughput so I can detect pipeline bottlenecks (PerformanceMetrics)  
* `validate_batch`          : Validate millions of samples in bulk and summarize invalid counts (BatchValidationInterface)  
* `set_default_values`      : Impute default values for missing numerical or categorical features (DefaultValues)  
* `validate_single`         : Quickly test individual data points and inspect exact failures (SingleItemValidation)  
* `conditional_validation`  : Ensure dependent validations, e.g., only check `rainfall` if `region=coastal` (ConditionalValidation)  
* `length_constraints`      : Enforce expected vector lengths for embeddings or lists of tags (LengthConstraints)  
* `optional_fields`         : Mark less-critical features as optional to tolerate sparse data (OptionalFields)  

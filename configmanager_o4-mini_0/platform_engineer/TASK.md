# The Task

I am a Platform Engineer building a multi-tenant configuration service.  
I want to register new config sources, enforce tenant-specific overrides, and allow our teams to hook into merge events to trigger deployments. This code repository will serve as the central merging engine, provide a plugin API, and guarantee predictable precedence across tenants and environments.

# The Requirements

* `register_plugin`       : Offer hooks to register custom config sources (e.g. database, HTTP endpoint), merge strategies, and notification mechanisms.  
* `merge_configs`         : Combine global defaults, tenant files, and per-tenant environment variables in a deterministic layer stack.  
* `set_precedence`        : Define precedence rules per source and per key so we can lock down sensitive settings at the platform level.  
* `select_profile`        : Support named profiles (e.g. tenantA, tenantB, shared) with overrides.  
* `export_to_ini`         : Export final merged configs to INI for integration with our legacy service managers.  
* `export_env_vars`       : Push final config into environment variables for sidecar processes.  
* `enable_hot_reload`     : Automatically reload and validate configurations when any tenant file or plugin changes.  
* `setup_logging`         : Emit structured logs describing who changed what, when, and how the merge turned out.  
* `cache_manager`         : Cache expensive computed values (e.g. computed ACL lists), invalidating on upstream changes.  
* `fetch_secret`          : Retrieve and merge secrets from Vault, AWS Secrets Manager, or Azure Key Vault per tenant.  

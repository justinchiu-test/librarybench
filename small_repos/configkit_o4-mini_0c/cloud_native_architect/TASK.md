# The Task

I am a cloud-native architect designing multi-tenant SaaS infrastructure. I need declarative, dynamic configuration that can adapt to each customer’s profile, enforce global guardrails, and stream changes to running clusters without downtime. This toolkit lets me unify TOML, YAML, and environment overlays into a coherent, validated configuration graph.

# The Requirements

* `resolve_variables` : Reference shared secrets and tenant-specific values via `${TENANT_DB_PASSWORD}` or `${global.rate.limit}`.  
* `load_toml`       : Ingest organization defaults from TOML blueprints.  
* `load_yaml`       : Load Helm values and service definitions from YAML.  
* `register_coercer`: Coerce custom types like `ResourceQuota`, `CPUQuantity`, and `RegionEnum`.  
* `register_hook`   : Pre-merge hook for schema validation, post-merge hook to enforce security policies, export hook to produce Terraform variable files.  
* `watch_and_reload`: Continuously watch config repos, trigger rolling updates when policies or workload limits change.  
* `merge_lists`     : Prepend global network policies, append tenant-specific ingress rules, ensure unique rule names.  
* `set_profile`     : Switch between `standard`, `enterprise`, and `compliance` profiles based on CLI flags or environment.  
* `get`             : Dot-notation retrieval of deeply nested resource settings (`cfg.get("tenants.123.network.egress")`).  
* `with_defaults`   : Fill defaults for optional SLA tiers and fallback capacity settings.  

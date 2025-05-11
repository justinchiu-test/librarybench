# The Task

I am a healthcare data engineer orchestrating clinical events—lab results, vitals, prescriptions—across multiple hospital systems. I want HIPAA-compliant encryption, rigorous schema validation, secure access controls, and audit-grade monitoring. This code repository empowers our integration platform with a pluggable, policy-driven event bus.

# The Requirements

* `<generateDocumentation>` : Auto-generate OpenAPI docs and type-safe client SDKs for EHR and analytics teams.  
* `<encryptPayload>`       : Enforce AES-256 and HSM-backed encryption for PHI in transit and at rest.  
* `<registerSerializer>`   : Support JSON, XML, and HL7 FHIR protobuf serializers/deserializers.  
* `<authorizeUser>`        : Role-based ACLs and OAuth2 token scopes to restrict topic access by department.  
* `<propagateContext>`     : Carry patient context (IDs, consent flags) and trace spans for comprehensive auditing.  
* `<balanceLoad>`          : Distribute workloads among validation and transformation services to optimize throughput.  
* `<validateSchema>`       : Validate all payloads against FHIR JSON Schema or Protobuf definitions before routing.  
* `<controlBackpressure>`  : Queue-size limits and configurable reject/drop policies to prevent hospital system overload.  
* `<setupClustering>`      : Multi-node active-active brokers with data replication for zero-downtime clinical operations.  
* `<exposeMetrics>`        : Provide JMX and Prometheus metrics—event counts, validation errors, processing latencies—for compliance dashboards.  

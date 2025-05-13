# The Task

I am a startup data analyst integrating multiple SaaS sources and building lightweight ETL scripts. I want a modular, plugin-friendly framework to add new connectors, serialize configs, orchestrate pipelines, and gracefully skip bad records. This code repository is an extensible ETL engine with pluggable stages, flexible serialization, and easy composition.

# The Requirements

* `PluginSystem` : Load new stage types, connectors, or serializers via separate packages with minimal coupling.
* `SourceSinkHooks` : Add custom hooks before and after reading or writing data to external systems for auditing or transformations.
* `JSONSerialization` : Serialize pipeline inputs, outputs, and intermediate states to JSON for interoperability with REST APIs.
* `YAMLSerialization` : Use YAML for human-friendly configuration files and clear version control diffs.
* `PipelineComposition` : Compose and reuse pipeline fragments declaratively, allowing complex workflow assembly from simple building blocks.
* `ErrorHandlingSkip` : Skip faulty records on stage failure and continue processing, with optional logging of error details for later inspection.

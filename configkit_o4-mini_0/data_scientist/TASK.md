# The Task

I am a data scientist tuning machine learning experiments. I want to declare my hyperparameters, data paths, and training schedules declaratively, override them per experiment, detect bad combos early, and even retrain automatically when I tweak a single value in my config file. This code repository is my experiment orchestration config backbone.

# The Requirements

* `DefaultFallback` : supply sensible defaults for learning rates, epochs, and batch sizes
* `TOMLLoader` : read experiment definitions from `experiments.toml` alongside code
* `EnvLoader` : let me inject secrets and data‐source URLs through `DS_` environment variables
* `ArgvLoader` : quickly override `learning_rate` or `model_name` via CLI when launching on a cluster
* `ConflictReporting` : detect conflicting schedules (e.g., two experiments writing to the same output path)
* `NestedMerge` : merge augmentation pipelines step by step but override full callbacks list
* `CustomCoercers` : parse date strings to `datetime`, durations (“30min”) to `timedelta`, and custom `Optimizer` enums
* `CLIConfigGenerator` : auto-generate a `train.py` CLI so all hyperparameters show up as flags with help text
* `ConfigWatcher` : attach callbacks that re‐launch training whenever my `data.path` or `batch_size` changes on disk
* `HotReload` : monitor my TOML/YAML config files in real‐time so parameter tweaks retrigger runs without restarting the notebook


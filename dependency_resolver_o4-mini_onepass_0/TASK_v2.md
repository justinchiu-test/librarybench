# The Task Updated

We want some updated functionality. Version 2 includes versioning support, dependency constraint solving, virtual environment management, lockfile generation, and package search. 

# New features to add:

Semantic Versioning Support

* Update `add_package(name, version, dependencies)` to support versioned dependencies.

Dependency Constraint Solver

* `install("A>=1.0,<3.0")` should pick the latest compatible version of A and resolve compatible versions of all dependencies recursively.

Virtual Environments

* Add `create_env(env_name)` and make installs/removals isolated per environment.
* Support `use_env(env_name)` to switch between environments.

Lockfile Generation

* Add `generate_lockfile(env_name)` that freezes all installed versions and writes them to a lock.json file.
* Add `install_from_lockfile(lockfile_path)` to reproduce a full environment.

Search / Query API

* `find_package(name, version_spec)` returns all matching versions in the registry.
* `why(name)` explains why a package was installed (e.g. as a dependency of what).
# The Task

I am a game developer building a live-tweakable game engine. I want to declare level parameters, AI behaviors, and asset paths in config files; override them per platform or environment; catch bad merge logic; and tweak values in real time while the game runs. This code repository is my dynamic config console.

# The Requirements

* `DefaultFallback` : define sensible defaults for physics parameters, spawn rates, and UI scales
* `TOMLLoader` : load level configs and script overrides from TOML files in the assets folder
* `EnvLoader` : let me override graphics settings via `GAME_` environment variables for CI builds
* `ArgvLoader` : parse `--level=2 --difficulty=hard` flags when launching the engine locally
* `ConflictReporting` : detect contradictory AI state machines or circular references in behavior trees
* `NestedMerge` : merge nested maps for `enemy.spawns` but override full arrays for `ambient.sounds`
* `CustomCoercers` : parse vector types, color enums, and duration literals into engine-native types
* `CLIConfigGenerator` : auto-generate a `gamectl` tool so designers can tweak every parameter from the terminal
* `ConfigWatcher` : register callbacks to reload only the lighting system when `graphics.shadow_quality` changes
* `HotReload` : watch asset config files so modifications appear instantly in the running game

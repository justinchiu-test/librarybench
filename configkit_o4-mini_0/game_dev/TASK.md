# The Task

I am a Game Developer tuning gameplay and server settings for an MMO. I want to be able to hot‐reload balance parameters, merge community‐provided mods safely, and produce docs for QA. This code repository supplies a dynamic, plugin‐based config system to keep my studios, mods, and live servers in sync.

# The Requirements

* `ConfigWatcher`         : subscribe to changes so I can hot‐reload weapon stats and NPC AI parameters in real time
* `VariableInterpolation` : reference `${default_speed}` or `${zones.${current_zone}.spawn_rate}` inside my YAML mod packs
* `ConfigVisualization`   : generate a graph of merged base, expansion, and community mod configs for QA review
* `DotNotationAccess`     : `cfg.get("weapons.sword.damage")` and `cfg.set("zones.ice.spawn_rate", 1.5)` from my level editor
* `NestedMerge`           : customize merges to append new items to loot tables but override quest scripts completely
* `ConflictReporting`     : detect and report mod‐to‐mod conflicts or circular references (e.g. mod A depends on mod B)
* `YAMLLoader`            : import base game and expansion configs from versioned YAML files
* `CustomCoercers`        : add coercers to parse color gradients, loot‐drop probabilities, and cooldown timers
* `ProfilesSupport`       : toggle between `development`, `staging`, and `live` server profiles
* `DefaultFallback`       : define fallback values so every NPC has a default AI state, even if a mod forgets one

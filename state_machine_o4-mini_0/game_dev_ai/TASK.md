# The Task

I am a game AI programmer building a non‐player character (NPC) behavior system. I want dynamic, nonblocking coroutines for patrol, chase, and idle states. This code repository empowers me to script complex state graphs, schedule timeouts (e.g. lose interest after 10 s), and test AI decision‐trees in isolation.

# The Requirements

* `enable_async_states` : let states, guards, and callbacks be coroutines so NPC routines yield control  
* `before_transition_global` : hook into every transition for universal animation blending setup  
* `after_transition_global` : hook into every transition to update blackboard and debug logs  
* `add_timeout_transition` : schedule auto‐transitions like “go to search” after a lose‐interest timeout  
* `create_cli_tooling` : ship CLI commands to scaffold new NPC machines, simulate patrol routes, and export graphs  
* `define_parallel_regions` : let NPC simultaneously handle movement and perception in orthogonal regions  
* `guard_function` : attach logical checks (e.g. player-in-sight?) to transitions  
* `compose_guard_set` : build complex conditions using AND/OR/NOT (e.g. low-health AND seeing-player)  
* `run_if` : execute callbacks (e.g. shout “Intruder!”) only when predicate on game context passes  
* `simulate_and_assert` : drive AI machines through event sequences, assert end‐states, stub out sound fx  
* `on_exit` : run cleanup (e.g. reset alert-level) whenever NPC leaves a pursuit state  

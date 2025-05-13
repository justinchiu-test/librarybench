# The Task

I am a game developer building a turn‐based RPG engine. I want to be able to model complex character and enemy behaviors as state machines, serialize them for network syncing and level editing, visualize them for debugging and design discussions, and support rollback on misplays. This code repository powers all of that.

# The Requirements

* `define_transition(name, src, dst, trigger)` : Declare named transitions (e.g. “attack”, “heal”) between states.
* `compose_guards(*guards, operator="AND")` : Combine multiple guard functions with AND/OR/NOT for conditional moves.
* `on_enter(state, callback)` : Register entry callbacks for applying status effects or animations.
* `add_global_hook(when, hook_fn)` : Define before/after-any-transition hooks (e.g. update UI or play SFX).
* `export_machine(format="json")` : Serialize character AI to JSON/YAML/dict for save files and multiplayer sync.
* `load_machine(serialized)` : Rehydrate serialized machines in the editor or on clients.
* `push_undo(event)` / `pop_undo()` : Undo/redo stack to backtrack turns or let players “undo” actions.
* `export_visualization(path="graph.dot")` : Emit Graphviz DOT or interactive diagram for level designers.
* `simulate_sequence(events)` : Testing harness to run event sequences and assert end states.
* `cli scaffold <machine_name>` : CLI utility to bootstrap new state machines.
* `cli visualize <machine_file>` : CLI to generate diagrams on the fly.
* `enable_history(state, mode="deep")` : Remember last active substate for nested boss phases.
* `run_tests()` : CLI command to run built‐in simulation tests on state logic.

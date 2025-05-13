# The Task

I am a robotics engineer orchestrating a warehouse automation system. I want to define precise robot behaviors—loading, transporting, avoiding collisions—simulate failure scenarios with undo/redo for safe testing, visualize workflows, and plug in global safety checks. This code repository is my core state machine framework.

# The Requirements

* `define_transition(name, src, dst, trigger)` : Model moves like “pickup→transport→dropoff” on sensor triggers.
* `compose_guards(guard_a, guard_b, operator="AND")` : Combine proximity and load‐capacity checks.
* `on_enter(state, callback)` : Fire routines when entering states (e.g. start motor, engage brakes).
* `add_global_hook("before", safety_check_hook)` : Run collision‐avoidance logic before any transition.
* `export_machine(format="yaml")` : Dump robot behavior to YAML for config management.
* `load_machine(yaml_str)` : Load updated behavior files without redeploying firmware.
* `push_undo(event)` / `pop_redo()` : Step back through simulated errors and replays.
* `export_visualization(format="dot")` : Generate Graphviz diagrams for floor‐layout planning.
* `simulate_sequence(events, assertions=True)` : Stress‐test event flows and assert safe end states.
* `cli run <machine_file>` : CLI tool to spin up robot state simulator.
* `cli scaffold <template>` : Quickly scaffold new machine templates.
* `enable_history("transport", mode="shallow")` : Track last known transport substate for efficient restarts.
* `run_tests()` : Execute integration tests in the simulation harness.

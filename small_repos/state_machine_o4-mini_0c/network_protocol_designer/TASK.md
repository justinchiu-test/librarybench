# The Task

I am a network protocol designer building a custom messaging handshake. I want to model states like SYN_SENT and ESTABLISHED, combine packet‐inspection guards, serialize the protocol spec, visualize the state chart, and thoroughly test edge cases with undo/replay. This code repo is my protocol state‐machine DSL.

# The Requirements

* `define_transition("SYN→ACK", "SYN_SENT", "ESTABLISHED", on_receive_synack)` : Model handshake steps.
* `compose_guards(check_checksum, validate_seq, operator="AND")` : Ensure packet integrity and ordering.
* `on_enter("ESTABLISHED", start_keepalive_timer)` : Kick off periodic keep‐alive.
* `add_global_hook("before", drop_if_invalid)` : Pre‐transition hook to filter bad packets.
* `export_machine("json")` : Dump the protocol spec for documentation and simulators.
* `load_machine(json_spec)` : Reload specs into test harnesses or routers.
* `push_undo(event)` / `pop_redo()` : Roll back or replay message sequences in simulation.
* `export_visualization("graphviz")` : Produce DOT files for RFC diagrams.
* `simulate_sequence(event_list, expected="ESTABLISHED")` : Validate protocol flows and handle retransmits.
* `cli scaffold protocol` : Create a new protocol spec from boilerplate.
* `cli visualize spec.json` : Quick‐look at protocol state graph.
* `enable_history("session", mode="shallow")` : Remember last substate in multiplexed sessions.
* `run_tests()` : Launch the full suite of simulation tests.

# The Task

I am a UX prototyper designing an interactive signup wizard. I want to wire up pages and transitions declaratively, mock user back/forward actions with undo/redo, export the flow to stakeholders, and write unit tests to catch regressions. This repo is my state‐machine prototyping tool.

# The Requirements

* `define_transition(name, from, to, trigger)` : Define “next”, “back”, “skip” transitions between wizard steps.
* `compose_guards(user_is_valid, has_agreed, operator="AND")` : Guard “submit” only if inputs pass.
* `on_enter("confirmation", show_summary)` : Hook to render summary page on entry.
* `add_global_hook("after", log_event)` : Log every transition for analytics.
* `export_machine(format="dict")` : Serialize the wizard flow to a dict for JSON‐RPC calls.
* `load_machine(dict_obj)` : Load saved designs into the interactive playground.
* `push_undo(event)` / `pop_undo()` : Simulate browser “Back” and “Forward” for user testing.
* `export_visualization(format="interactive")` : Create an embeddable flowchart for stakeholder review.
* `simulate_sequence(["next","back","next"], expect_states=["step2","step1","step2"])` : Automated UI tests.
* `cli scaffold wizard` : Scaffold a new wizard flow from templates.
* `cli dump-state session_id` : Inspect current machine state in terminal.
* `enable_history("step_group", mode="deep")` : Remember last sub‐step when re‐entering multi‐page sections.
* `run_tests()` : Run built‐in simulation suite to catch broken flows.

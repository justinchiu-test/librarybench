# The Task

I am a business process analyst modeling order‐to‐cash workflows. I want to define transitions for order approval, shipment, invoicing; serialize to YAML for process automation tools; visualize flows for stakeholders; simulate “what‐if” scenarios with undo/redo; and embed global compliance checks. This code repo is my process‐modeling engine.

# The Requirements

* `define_transition("approve_order", "pending", "approved", on_manager_approval)` : Capture key process steps.
* `compose_guards(has_budget, is_compliant, operator="AND")` : Enforce budget and regulatory checks.
* `on_enter("invoiced", send_invoice_email)` : Trigger invoicing callbacks.
* `add_global_hook("after", audit_log_hook)` : Append every transition to compliance logs.
* `export_machine("yaml")` : Serialize workflows to YAML for RPA tools.
* `load_machine(yaml_str)` : Import updated processes into the orchestrator.
* `push_undo(event)` / `pop_undo()` : Roll back simulated runs in “what‐if” analyses.
* `export_visualization("dot")` : Generate Graphviz charts for stakeholder reviews.
* `simulate_sequence(["approve","ship","invoice"], assert_final="completed")` : Test edge cases like partial shipments.
* `cli scaffold process` : Kick off a new process model.
* `cli dump-state process_id` : Inspect state mid‐simulation.
* `enable_history("order_group", mode="deep")` : Remember last sub‐process in multistage orders.
* `run_tests()` : Execute built‐in scenario simulations and compliance checks.

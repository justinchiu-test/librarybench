# The Task

I am a distributed systems engineer modeling an order‐processing workflow. I want to orchestrate microservice states, enforce retries, timeouts, and run global audits. This code repository provides a robust FSM framework to compose guards, schedule deadline‐driven transitions, and run end‐to‐end simulations before deployment.

# The Requirements

* `async_await_support` : define coroutine callbacks and guards for nonblocking network calls  
* `register_global_before` : add a hook before any transition for audit‐trail and metrics collection  
* `register_global_after` : add a hook after any transition to publish events to Kafka  
* `timeout_transition` : automatically move orders to “failed” if payment isn’t confirmed by deadline  
* `cli_scaffold_machine` : CLI commands to build new workflows, run dry‐run simulations, and visualize state graphs  
* `parallel_regions` : model independent shipping, billing, and notifications in concurrent regions  
* `add_guard_function` : attach business‐rule predicates (e.g. credit-check-passed?) to transitions  
* `compose_guards_logic` : combine multiple checks with AND/OR/NOT for multi‐factor rules  
* `conditional_callback` : invoke reconciliation hooks only when certain context flags are true  
* `testing_simulation_harness` : simulate event flows, assert final states, and stub external service calls  
* `exit_callback` : register cleanup tasks when leaving “processing” state (e.g. rollback reservations)  

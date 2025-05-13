# The Task

I am a home automation engineer designing an intelligent lighting and climate control system for a smart house. I want to define device states, orchestrate asynchronous sensor readings, and handle cross‐cutting safety checks. This code repository gives me a state-machine library to declare device modes, enforce transition constraints, simulate schedules, and deploy reliable automations without blocking the main control loop.

# The Requirements

* `async_transition` : support async/await guards, callbacks, and event dispatch so sensor I/O never blocks  
* `add_global_before_hook` : register “before any transition” logic for logging and system‐wide safety checks  
* `add_global_after_hook` : register “after any transition” logic to update dashboards and notify services  
* `define_timeout` : fire transitions automatically after a specified duration (e.g. “turn off lights after 30 min”)  
* `scaffold_cli` : generate new machine definitions, simulate scenarios, dump current state, and render diagrams  
* `add_region` : define parallel regions for heating, cooling, and lighting to run concurrently  
* `add_guard` : attach predicate functions (e.g. is-window-open?) to conditionally allow transitions  
* `compose_guards` : combine multiple guards with AND, OR, NOT for complex safety rules  
* `conditional_callback` : call notification hooks only when thresholds (e.g. temperature > 75°F) are reached  
* `test_harness` : simulate event sequences, assert machine reaches “eco mode,” and stub out real PLC callbacks  
* `on_exit_state` : register cleanup or rollback logic whenever a device state (e.g. “ventilation”) is exited  

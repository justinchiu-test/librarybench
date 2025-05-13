# The Task

I am a QA automation specialist building a comprehensive test suite for event‐driven systems. I want to validate complex state transitions, guard logic, and timeouts. This code repository gives me a testing and simulation framework to assert all state graphs behave as expected under various scenarios.

# The Requirements

* `use_async_guards` : test guards and callbacks implemented as coroutines without blocking the test runner  
* `set_global_before_hook` : verify cross‐cutting pre‐transition hooks fire consistently across machines  
* `set_global_after_hook` : ensure global post‐transition analytics hooks run for every state change  
* `define_timeout_event` : test that transitions fire when deadlines expire (e.g. session‐timeout)  
* `cli_run_tests` : leverage CLI to scaffold test harnesses, run batch simulations, and capture outputs  
* `enable_parallel_tests` : simulate orthogonal state regions simultaneously in one test scenario  
* `apply_guard` : attach dummy guards to transitions and assert correct blocking/allowing behavior  
* `chain_guards` : test AND/OR/NOT guard compositions systematically  
* `conditional_exec` : confirm that callbacks only execute under specified predicate conditions  
* `simulation_helpers` : stub events, drive sequences, assert states, and mock external callbacks  
* `on_exit_callback_test` : register and verify exit callbacks fire when leaving target states  

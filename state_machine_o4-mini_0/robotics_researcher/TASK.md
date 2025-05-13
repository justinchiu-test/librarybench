# The Task

I am a robotics researcher implementing a multi‐legged robot’s gait controller. I want to coordinate asynchronous sensor feedback, concurrency across limb controllers, and automatic fall‐recovery transitions. This code repository equips me with a flexible state‐machine to express parallel locomotion phases, safety guards, and test‐driven simulations.

# The Requirements

* `allow_async` : support async/await for nonblocking sensor reads and actuation commands  
* `global_before_transition` : define pre‐transition checks (e.g. check battery level) for all moves  
* `global_after_transition` : define post‐transition hooks to log joint trajectories  
* `transition_after_timeout` : auto‐trigger “stop gait” if no foot contact detected after threshold  
* `cli_tools` : provide CLI to scaffold gait machines, run step‐by‐step sims, and export timing diagrams  
* `parallel_limb_regions` : run state machines for front and rear legs in separate regions concurrently  
* `attach_guard` : add predicate functions (e.g. is‐terrain‐stable?) to block unsafe moves  
* `guard_composition` : combine multiple safety checks (e.g. joint‐torque OK AND terrain stable)  
* `conditional_on` : fire especially risky maneuvers only when context predicates pass  
* `simulation_harness` : drive simulated footfall sequences, assert stability, and stub motor drivers  
* `on_exit_gait` : register fallback logic whenever exiting a walking gait to recover posture  

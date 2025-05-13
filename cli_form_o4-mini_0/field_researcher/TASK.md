# The Task

I am a field researcher conducting surveys in offline, low‐bandwidth environments on remote terminals. I want an interactive form that validates responses in real time, branches questions based on prior answers, and saves progress to local storage. This code repository gives me a curses UI, offline session support, dynamic skip logic, and full audit logs for my data collection workflow.

# The Requirements

* `real_time_validate()`  : Immediate range checks on numerical inputs (e.g., age, temperature).  
* `apply_skip_logic()`    : Skip environment questions if respondent selects “Indoors.”  
* `navigate()`            : next/prev commands, jump to any question, back/forward history, boundary checks.  
* `enable_accessibility_mode()` : High‐contrast and screen‐reader text cues for visually impaired respondents.  
* `init_curses_renderer()`: Full‐screen terminal UI with navigation hints and status bar showing battery/time.  
* `audit_log_event()`     : Timestamped record of each answer, edit, skip, and validation error.  
* `start_wizard()`        : Organize 50 questions into logical pages (Demographics → Environment → Feedback).  
* `save_session()` / `load_session()` : Persist responses locally and resume after power cycles.  
* `register_plugin()`     : Add a custom “geolocation picker” field to capture GPS coordinates from handheld device.  
* `branch_flow()`         : Reorder follow‐up modules based on preliminary health‐risk answers.  

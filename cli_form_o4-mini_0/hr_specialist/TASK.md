# The Task

I am an HR specialist responsible for onboarding new employees across global offices. I want to run an interactive terminal form that guides hiring managers through benefits enrollment, equipment requests, and compliance acknowledgments—while ensuring accessibility and saving partial progress. This code repository delivers a rich, accessible CLI wizard with branching logic, validation, and full audit trails.

# The Requirements

* `real_time_validate()`  : Instant email, SSN, and phone number formatting checks as managers type.  
* `apply_skip_logic()`    : Hide pension plan questions if the hire is part‐time or contractor.  
* `navigate()`            : Standard next/previous, jump to “Benefits” or “Equipment” sections, history stack, boundary checks.  
* `enable_accessibility_mode()` : ARIA‐style announcements, keyboard‐only navigation, and high‐contrast theme.  
* `init_curses_renderer()`: Polished curses‐based UI with clear section headers and status bar.  
* `audit_log_event()`     : Record every change, skip, and page view for compliance reporting.  
* `start_wizard()`        : Multi‐page wizard (Personal Info → Benefits → Equipment → Review).  
* `save_session()` / `load_session()` : Let busy managers quit mid‐way and pick up later.  
* `register_plugin()`     : Add a custom “office location picker” field that queries our internal API.  
* `branch_flow()`         : Entire “Relocation Assistance” page surfaces only if “Relocate” is yes.  

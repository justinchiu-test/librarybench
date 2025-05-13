# The Task

I am a plugin developer building custom field types for a variety of CLI surveys. I want a clear extension API so I can author new widgets—like date‐pickers, file selectors, or color wheels—that integrate seamlessly with validation, navigation, and session management. This code repository offers the hooks, events, and renderer abstractions I need.

# The Requirements

* `real_time_validate()`  : Hook into input streams to flag invalid widget values live.  
* `apply_skip_logic()`    : Plug into the skip logic engine to show/hide my custom fields.  
* `navigate()`            : Respect next/prev/jump semantics and integrate with breadcrumb history.  
* `enable_accessibility_mode()` : Ensure my widgets expose ARIA labels and high‐contrast styling.  
* `init_curses_renderer()`: Leverage the curses renderer to draw custom windows and input areas.  
* `audit_log_event()`     : Emit logs for every interaction with my plugin fields.  
* `start_wizard()`        : Integrate my widgets within multi‐page wizards and progress bars.  
* `save_session()` / `load_session()` : Persist plugin‐specific state alongside core form data.  
* `register_plugin()`     : Minimal boilerplate to register field types, renderers, validators, and callbacks.  
* `branch_flow()`         : Participate in complex branching so my fields can appear or shuffle order based on earlier answers.  

# The Task

I am a product manager. I want to run quick internal surveys from the command line during stand-ups or hackathons. This code repository lets me build multi-step wizards with custom ratings, instant feedback, and exportable results.

# The Requirements

* `validate_input` : Real-Time Validation Feedback to ensure required questions are answered and numeric ratings are in range  
* `curses_renderer` : Curses-Based Renderer providing status bars, tab groups, and embedded help pop-ups  
* `text_field`    : Text Field Type with length limits and placeholders for open-ended feedback  
* `wizard_layout` : Multi-Page Wizard Layouts to step participants through “Intro → Questions → Comments → Submit”  
* `format_error`  : Customizable Error Formatting to show inline warnings on skipped mandatory questions  
* `date_time_picker` : Date & Time Picker Field Type for scheduling survey reminders or live feedback sessions  
* `enable_accessibility_mode` : Accessibility Mode so every team member, including those using screen-readers, can participate  
* `audit_log`     : Audit Logging & Change History to track who changed survey questions or skipped steps  
* `register_field_plugin` : Plugin API for Custom Fields (e.g., emoji rating widget or file attachment selector)  
* `export_data`   : Data Export Utilities to output survey results as JSON or YAML for our BI dashboard  

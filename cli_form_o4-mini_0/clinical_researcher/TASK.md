# The Task

I am a clinical researcher. I want to collect standardized patient intake data on hospital terminals so that data is validated at entry, fully auditable, and easily exported for analysis. This code repository provides a full-screen, accessible form system with date-of-birth pickers and custom error messages.

# The Requirements

* `validate_input` : Real-Time Validation Feedback for patient IDs, phone numbers, and required fields  
* `curses_renderer` : Curses-Based Renderer with tab-navigable windows, labels, and context help  
* `text_field`    : Text Field Type supporting regex for SSN, max-length on name fields, and placeholder text  
* `wizard_layout` : Multi-Page Wizard Layouts dividing the form into “Demographics → History → Consent → Review”  
* `format_error`  : Customizable Error Formatting to highlight missing consent checkboxes or invalid dates  
* `date_time_picker` : Date & Time Picker Field Type for birth dates and appointment times with calendar view  
* `enable_accessibility_mode` : Accessibility Mode for screen-reader friendly prompts and high-contrast themes  
* `audit_log`     : Audit Logging & Change History to ensure HIPAA-compliant record of every change and navigation  
* `register_field_plugin` : Plugin API for Custom Fields in case we need a medical code picker or image uploader  
* `export_data`   : Data Export Utilities to dump patient records as JSON, YAML, or Python dict for downstream ETL  

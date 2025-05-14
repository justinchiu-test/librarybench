# The Task

I am an HR Manager implementing a candidate evaluation CLI tool for on‐the‐fly interview feedback. I want a flexible, interactive form that lets me enter candidate info, select skills ratings, add notes, and confirm the review before committing it to our database. This code repository is the form engine I need to prototype and deploy that tool quickly.

# The Requirements

* `ask_text` : Single-line input for candidate name, position, or short summary, with configurable length limits, regex patterns for email, and placeholder hints.
* `branch_flow` : Dynamic sections that appear based on role type (engineering vs marketing), adjusting question order and fields accordingly.
* `load_choices_async` : Fetch live job openings, interviewers, or skill categories from the HR API, with visible loading indicators and local caching.
* `input_line_fallback` : A pure-stdin/stdout prompt mode for remote access via SSH or when curses libraries are unavailable.
* `review_submission` : A confirmation screen summarizing all feedback entries—ratings, notes, and flags—with inline editing before saving.
* `ask_password` : Securely enter admin credentials or API tokens, with optional strength feedback and show/hide toggle.
* `select_choices` : Choice list for rating skills (1–5 stars) or selecting multiple interview rounds, controlled via arrow keys.
* `set_renderer_theme` : Plug in custom color palettes and border styles to match the company’s internal CLI branding.
* `register_on_change` : Hooks that recalculate overall score or suggest next questions when an individual rating changes.
* `format_errors` : Customizable error message templates that highlight missing fields or invalid ratings using colors and inline hints.


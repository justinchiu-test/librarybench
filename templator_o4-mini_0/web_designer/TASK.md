# The Task

I am a web designer building a dynamic site with user-customizable themes. I want to be able to write templates that can safely execute small expressions, include or extend other templates, and stream large pages (like image galleries) without holding everything in memory. This code repository provides a secure, flexible, and high-performance templating engine for HTML/XML sites.

# The Requirements

* `safe_eval`         : Evaluate only literals and simple operations (via `ast.literal_eval`) to prevent injection.
* `render_stream`     : Return templates as an iterator/generator so I can stream chunk by chunk.
* `scoped_context`    : Maintain nested variable scopes in loops/includes so nothing leaks out.
* `to_json`           : Convert Python objects to JSON for embedding in `<script>` blocks.
* `from_json`         : Parse JSON snippets back into data structures.
* `to_yaml`           : Dump data as YAML (e.g. site metadata).
* `from_yaml`         : Load YAML front-matter safely.
* `report_error`      : Show syntax/parse/runtime errors with file name, snippet, and accurate line number.
* `autoescape`        : Escape HTML/XML by default to avoid XSS.
* `raw`               : Disable escaping when I want raw HTML insertion.
* `trim_tags`         : Control whitespace around tags using `{{- … -}}` or `{%- … -%}`.
* `define_macro`      : Create reusable template functions (e.g. nav bar, footer).
* `set_delimiters`    : Swap default `{% %}` and `{{ }}` for `<% %>` or other markers.
* `add`, `sub`, `mul`, `div`  : Do simple math in templates (e.g. `{{ items|count|add(1) }}`).
* `is_even`, `is_odd`          : Test numbers for conditional styling or row-striping.
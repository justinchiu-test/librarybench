# The Task

I am a data analyst generating HTML/Markdown reports with embedded charts and raw data dumps. I want to embed JSON data for D3.js, convert tables to YAML for front-matter, and use macros for chart boilerplate. This code repository gives me safe evaluation and advanced filters so I can produce reproducible, streamed reports without security holes.

# The Requirements

* `safe_eval`         : Only allow literal expressions in report templates.
* `render_stream`     : Stream long tables and chart data to the client.
* `scoped_context`    : Isolate loop variables in table and chart macros.
* `to_json`           : Serialize analysis results for client-side charts.
* `from_json`         : Load external JSON snippets.
* `to_yaml`           : Dump metadata or config in YAML front-matter.
* `from_yaml`         : Read YAML blocks from data files.
* `report_error`      : Show parse/runtime errors with context snippets.
* `autoescape`        : Escape Markdown/HTML by default when including user data.
* `raw`               : Insert raw SVG or code blocks unescaped.
* `trim_tags`         : Manage whitespace so Markdown formatting isn’t broken.
* `define_macro`      : Write chart macros (`bar_chart`, `line_chart`).
* `set_delimiters`    : Switch to `<<% %>>` if `{{ }}` conflicts with other tooling.
* `add`, `sub`, `mul`, `div`  : Calculate percentages or aggregates inline.
* `is_even`, `is_odd`          : Alternate row colors in table outputs.
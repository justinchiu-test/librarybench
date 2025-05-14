# The Task

I am a security researcher creating proof-of-concept templates to test sandbox bypasses. I want a locked-down evaluator, detailed error reports, and the ability to tweak delimiters and scopes for pen-testing. This code repository offers robust sandboxing and introspection hooks.

# The Requirements

* `safe_eval`         : Strict AST literal evaluation; no attribute access or function calls.
* `render_stream`     : Observe buffer sizes and streaming behavior for timing attacks.
* `scoped_context`    : Ensure inner scopes cannot mutate outer data.
* `to_json`           : Embed test payloads safely in JSON.
* `from_json`         : Parse responses for fuzz testing.
* `to_yaml`           : Insert YAML payloads for injection tests.
* `from_yaml`         : Load crafted YAML snippets under sandbox.
* `report_error`      : Capture full trace with code snippets & accurate lines.
* `autoescape`        : Force-on escaping to block XSS vectors.
* `raw`               : Explicitly disable escaping only where I choose.
* `trim_tags`         : Test whitespace trimming edge cases.
* `define_macro`      : Create exploit patterns as macros.
* `set_delimiters`    : Switch delimiters to bypass naive filters.
* `add`, `sub`, `mul`, `div`  : Confirm arithmetic cannot be misused.
* `is_even`, `is_odd`          : Validate boolean test safety.
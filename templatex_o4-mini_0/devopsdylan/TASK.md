# The Task

I am a DevOps engineer templating configuration files across dozens of services. I want to be able to generate YAML, JSON, and shell scripts reliably, safely, and quickly. This code repository provides me with context-aware escaping, streaming, build integration, and sandbox controls so I can automate deployments without risking malformed configs or security holes.

# The Requirements

* `escape(mode, text)` : Automatic escaping for shell commands, JSON payloads, and HTML status pages to prevent injection and syntax errors.  
* `minify(template)`    : Collapse whitespace and strip comments from rendered configuration snippets for leaner artifacts.  
* `build_graph()`       : Expose dependency graph of include/import relationships to optimize CI/CD pipeline caching.  
* `render_expr(expr)`   : Evaluate arithmetic, comparison, and boolean logic within templates for dynamic values.  
* `if_block(cond, then_, elifs, else_)` : Flexible conditional blocks (`{% if … %}`, `{% elif … %}`, `{% else %}`, `{% endif %}`).  
* `stream_render(template)` : Stream-render large config files or logs to reduce memory footprint during generation.  
* `assert_render(template, context, expected)` : Unit-test template output against expected config fragments.  
* `profile_render(template, context)`   : Collect timing for parsing, compilation, and rendering to diagnose slow template issues.  
* `enable_sandbox()`    : Lock down template execution so untrusted inputs cannot run arbitrary Python code.  
* `precompile(template)` : Precompile templates to AST and cache them for lightning-fast repeat runs in automation scripts.  

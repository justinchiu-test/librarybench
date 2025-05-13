# The Task

I am a performance engineer optimizing our templating layer under heavy traffic. I want to be able to measure parse/compile/render timings, preprocess and cache templates, and adjust dependency graphs so we render millions of pages per hour with minimal latency. This code repository equips me with profiling, precompilation, streaming, and build hooks to squeeze out every millisecond.

# The Requirements

* `escape(mode, text)` : Fast, built-in escaping for HTML, JSON, and shell contexts to avoid rolling-my-own slow filters.  
* `minify(template)`    : High-speed whitespace stripping and comment removal for production builds.  
* `build_graph()`       : Expose template import/include relationships for parallel compilation and incremental builds.  
* `render_expr(expr)`   : Inline evaluation of Pythonic expressions with minimal overhead.  
* `if_block(cond, then_, elifs, else_)` : Optimized branching constructs (`{% if %}`, `{% elif %}`, `{% else %}`, `{% endif %}`).  
* `stream_render(template)` : Generator-based streaming of output to reduce end-to-end latency under load.  
* `assert_render(template, context, expected)` : Automated test harness to guard performance regressions in render output.  
* `profile_render(template, context)`   : Fine-grained instrumentation of parsing, AST compilation, and rendering phases.  
* `enable_sandbox()`    : Sandbox mode to safely benchmark user-provided templates without side effects.  
* `precompile(template)` : AST precompilation and caching for constant-time template lookups at runtime.  

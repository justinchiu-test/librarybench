# The Task

I am a web developer building a multi-tenant CMS. I want to be able to write modular, secure page templates that integrate smoothly into my build pipeline. This code repository gives me a unified templating engine with built-in security, optimization, and test utilities so I can ship fast without worrying about injection bugs or slow pages.

# The Requirements

* `escape(mode, text)` : Built-in escaping modes for HTML, JSON, and shell contexts to mitigate XSS and injection risks.  
* `minify(template)`    : Post-render filter to strip comments, collapse whitespace, and compress HTML/CSS for production.  
* `build_graph()`       : Analyze upstream/downstream relationships between templates for incremental rebuilds.  
* `render_expr(expr)`   : Evaluate simple Pythonic expressions (`{{ a + b }}`, comparisons, boolean ops) directly in templates.  
* `if_block(cond, then_, elifs, else_)` : Conditional blocks with `{% if %}`, `{% elif %}`, `{% else %}`, `{% endif %}` logic.  
* `stream_render(template)` : Stream output in chunks to the client as it’s generated, avoiding large buffers.  
* `assert_render(template, context, expected)` : Integrated test harness to write assertions on rendered output in unit tests.  
* `profile_render(template, context)`   : Instrument parsing, compilation, and rendering for performance metrics and bottleneck analysis.  
* `enable_sandbox()`    : Restrict Python built-ins and globals so untrusted template code cannot execute arbitrary operations.  
* `precompile(template)` : Parse templates into an AST once, cache the compiled code, and reuse for ultra-fast rendering.  

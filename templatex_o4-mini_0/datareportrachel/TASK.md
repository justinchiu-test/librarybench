# The Task

I am a data analyst generating large HTML and CSV reports. I want to be able to inject dynamic tables, charts, and pagination logic into my templates without writing low-level code. This code repository gives me an expressive, secure template language with streaming, minification, and built-in testing so I can iterate on reports rapidly and deploy them at scale.

# The Requirements

* `escape(mode, text)` : Context-aware escaping for HTML cells, JSON chart data, or shell-invoked report generators.  
* `minify(template)`    : Post-render compression to strip comments and collapse whitespace in HTML/CSS reports.  
* `build_graph()`       : Graph the dependencies between master layouts and subreports for efficient rebuilds.  
* `render_expr(expr)`   : Use inline Pythonic expressions to compute sums, averages, and conditional values.  
* `if_block(cond, then_, elifs, else_)` : Advanced branching with `{% if … %}`, `{% elif … %}`, `{% else %}`, `{% endif %}`.  
* `stream_render(template)` : Stream CSV rows or HTML chunks as they render to avoid loading millions of records in memory.  
* `assert_render(template, context, expected)` : Test tables, totals, and markup in unit tests before scheduling nightly jobs.  
* `profile_render(template, context)`   : Profile parsing, AST generation, and render loops to find slow queries or loops.  
* `enable_sandbox()`    : Run untrusted or user-provided report templates safely without exposing internal data or functions.  
* `precompile(template)` : Cache AST-based compiled templates so repeated report runs start instantly.  

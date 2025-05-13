# The Task

I am a security engineer auditing and hardening our templating system. I want to be able to enforce strict escaping, sandboxing, and inspect performance to ensure no injection or denial-of-service vulnerabilities slip through. This code repository provides fine-grained controls, metrics, and test harnesses so I can verify that every template is safe and performant.

# The Requirements

* `escape(mode, text)` : Enforce built-in escaping for HTML, JSON, and shell contexts to nullify injection risk.  
* `minify(template)`    : Optionally compress and strip comments to reduce attack surface in client-served HTML.  
* `build_graph()`       : Expose template dependency graph for impact analysis when changes occur.  
* `render_expr(expr)`   : Permit only safe Pythonic expressions (arithmetic, boolean ops) in templates.  
* `if_block(cond, then_, elifs, else_)` : Controlled branching logic with explicit start/end tags.  
* `stream_render(template)` : Stream output safely to avoid server OOMs from maliciously large templates.  
* `assert_render(template, context, expected)` : Write security and correctness assertions as unit tests.  
* `profile_render(template, context)`   : Monitor parse/compile/render phases for anomalous latencies or resource spikes.  
* `enable_sandbox()`    : Strict sandbox/safe mode that restricts Python built-ins, globals, and I/O calls.  
* `precompile(template)` : Precompile to AST and cache, preventing on-the-fly code injections or rogue evals.  

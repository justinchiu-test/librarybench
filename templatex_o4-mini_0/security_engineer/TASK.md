# The Task

I am a security engineer responsible for vetting third-party templates used by various teams. I want a robust safe-mode sandbox, granular profiling of template–engine internals, and strict escaping rules. I also need the ability to include policy snippets, cache vetted rulesets, and provide custom sanitizers for specialized contexts. This code repo is my hardened template execution environment.

# The Requirements

* `enable_sandbox_mode` : Tight sandbox to restrict Python built-ins, file I/O, and network calls in untrusted templates.  
* `include(policy_snippet)` : Securely embed policy fragments, default headers, or compliance notices.  
* `cache_template(policy_snippet)` : Cache audited templates to avoid re-validation on every render.  
* `render_stream(policy_snippet, ctx)` : Stream logs or rule dumps securely without full buffering.  
* `escape_html(value)` / `escape_json(value)` / `escape_shell(value)` : Context-aware escaping to prevent injection in any vector.  
* `dot_lookup(ctx, 'user.meta.roles')` : Fine-grained nested context access for policy decisions.  
* `minify(output)` : Compact sanitized output to eliminate comment-based exfiltration channels.  
* `default_filter(value, default)` : Fallback values for missing policy variables (`{{ expiration|default('never') }}`).  
* `add_filter('sanitize_xss', func)` : Custom filters to enforce additional sanitization layers or inline WAF rules.  
* `profile_render(policy_snippet)` : Collect metrics for audit trails, showing parse, compile, and render timings per template.  

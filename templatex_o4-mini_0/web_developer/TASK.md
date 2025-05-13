# The Task

I am a frontend web developer for a fast-growing SaaS product. I want to be able to build and maintain a high-performance, secure templating layer for our web application that supports complex layouts, partials, and automatic contextual escaping, while giving designers enough freedom to drop in snippets without worrying about downtime or XSS vulnerabilities. This code repository is my one-stop template engine that ticks all the boxes for modern web development and performance tuning.

# The Requirements

* `enable_sandbox_mode` : Restrict Python built-ins and globals so untrusted designer templates cannot execute arbitrary code.  
* `include(template_name)` : Support partials and includes (`{% include 'header.tpl' %}`) for modular layouts and shared snippets.  
* `cache_template(template_name)` : In-memory or on-disk caching of compiled templates to reduce parse time on repeated renders.  
* `render_stream(template_name, context)` : Streaming output via generators for large page fragments or long polling responses.  
* `escape_html(value)` / `escape_json(value)` / `escape_shell(value)` : Automatic built-in escaping modes for HTML, JSON, and shell contexts to mitigate injection risks.  
* `dot_lookup(context, 'user.profile.name')` : Dot-notation context access for nested lookups in templates.  
* `minify_html(output)` : Post-render minification and compression to strip comments, collapse whitespace, and optimize payload size.  
* `default_filter(value, default)` : Fallback for undefined or null variables (`{{ user.name|default('Guest') }}`).  
* `add_filter('format_date', func)` : Register custom filters such as date formatting, slugify, or currency formatting.  
* `profile_render(template_name)` : Profiling and metrics for parse, compile, and render phases to diagnose performance bottlenecks.  

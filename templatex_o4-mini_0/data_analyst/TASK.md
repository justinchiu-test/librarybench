# The Task

I am a data analyst building on-the-fly HTML and JSON reports. I want to be able to craft templates that join charts, tables, and raw CSV dumps into single pages or API endpoints, with rich helper functions, streaming for huge datasets, and built-in escaping so I don't accidentally produce XSS in our BI portal. This code repo is my flexible reporting engine.

# The Requirements

* `enable_sandbox_mode` : Ensure that user-written report templates cannot run arbitrary Python when previewed in the browser.  
* `include(template_name)` : Mix and match chart headers, footers, and table blocks via includes for consistent styling.  
* `cache_template(template_name)` : Pre-compile report templates so daily dashboards render in milliseconds.  
* `render_stream(template_name, context)` : Output row by row for tables with millions of records without blowing memory.  
* `escape_html(value)` / `escape_json(value)` : Contextual escaping to protect our BI web-UI and JSON-based API clients.  
* `dot_lookup(context, 'metrics.monthly[0].value')` : Simple dot-notation access to nested data frames or config entries.  
* `minify_html(output)` : Collapse whitespace and strip comments for sleek report pages.  
* `default_filter(value, default)` : Graceful defaults for missing data points (`{{ sales|default(0) }}`).  
* `add_filter('pretty_date', func)` : Register custom filters like date formatting, number rounding, or percentile calculation.  
* `profile_render(template_name)` : Detailed timing breakdown of parsing vs. rendering vs. filter conversion.  

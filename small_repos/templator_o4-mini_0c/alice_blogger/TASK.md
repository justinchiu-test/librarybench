# The Task

I am a tech blogger who needs to assemble dynamic, data-driven posts with date stamps, code snippets and simple calculated values. I want to author templates that pull in JSON front-matter, perform small arithmetic on the fly (like “posts per month”), show “time ago” for comments, and support live editing without restarting my server. This code repository gives me a full-featured templating engine with filters, control logic, inheritance, caching, streaming, i18n and automatic reload in development.

# The Requirements

* `add`            : adds two numbers in a template  
* `sub`            : subtracts one number from another  
* `mul`            : multiplies two values  
* `div`            : divides one value by another  
* `is_even`        : tests whether a number is even  
* `is_odd`         : tests whether a number is odd  
* `date(format)`   : formats a datetime object according to a pattern  
* `timeago()`      : renders a “time ago” string (e.g. “3 hours ago”)  
* `strftime`       : wraps Python’s strftime for custom date formatting  
* `to_json`        : serializes a data object to JSON for embedding  
* `from_json`      : parses a JSON string into a native object  
* `to_yaml`        : serializes a data object to YAML  
* `from_yaml`      : parses a YAML string into a native object  
* `render_stream`  : returns a generator to stream large pages chunk by chunk  
* `extends`        : specify a base template to inherit from  
* `block`          : define named regions that child templates can override  
* `cache_template` : cache parsed or compiled templates in memory  
* `trans`          : mark literal text for translation in-template  
* `gettext`        : integrate translations via gettext catalogs  
* `auto_reload`    : detect template file changes and reparse on the fly  
* `if` / `elif` / `else` : control flow tags for conditional rendering  
* `for` / `endfor`        : loop over collections in the template  
* `syntax_highlight` : produce colored or annotated syntax errors for easy debugging  

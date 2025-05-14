# The Task

I am a DevOps engineer automating deployment dashboards and status pages. I want templates that show service uptime, compute simple SLO percentages, display “last updated” relative times, and allow me to inject JSON-formatted health check data. I need template inheritance for consistent layouts, fast caching in production, auto-reload during design, and streaming for large logs. This code repo is my one-stop templating solution.

# The Requirements

* `add`            : calculate total downtime minutes  
* `sub`            : subtract maintenance windows  
* `mul`            : compute scaled metrics (e.g. per-node)  
* `div`            : derive uptime percentages  
* `is_even`        : style alternate log lines  
* `is_odd`         : highlight error rows  
* `date(format)`   : format deployment timestamps  
* `timeago()`      : show “X minutes ago” for health checks  
* `strftime`       : custom timestamp patterns  
* `to_json`        : embed JSON health-check payloads  
* `from_json`      : parse incoming service data  
* `to_yaml`        : store config dumps inline  
* `from_yaml`      : read YAML alerts from files  
* `render_stream`  : stream live log output  
* `extends`        : reuse base dashboard template  
* `block`          : override metrics or graph regions  
* `cache_template` : speed up repeated render in production  
* `trans`          : mark UI messages for multi-region ops  
* `gettext`        : use existing po/mo files for translation  
* `auto_reload`    : automatically reload changed templates in staging  
* `if` / `elif` / `else` : show/hide sections based on environment  
* `for` / `endfor`        : list services, alerts or nodes  
* `syntax_highlight` : annotated syntax error feedback in CI logs  

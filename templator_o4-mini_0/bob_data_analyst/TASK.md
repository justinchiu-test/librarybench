# The Task

I am a data analyst who needs to generate CSV and HTML reports from Python scripts. I want to embed complex data structures, run simple math in the template, group and filter rows, and export to JSON and YAML. I also want the ability to preview huge reports as a stream, cache templates between runs, and tweak templates without restarting my notebook. This repository gives me everything I need in a single templating library.

# The Requirements

* `add`            : compute summary metrics (totals, increments)  
* `sub`            : compute differences (deltas)  
* `mul`            : multiply fields for weighted averages  
* `div`            : divide safely (e.g. avoid zero-division)  
* `is_even`        : test row indices or counts for evenness  
* `is_odd`         : test indices for odd/even styling  
* `date(format)`   : format timestamps on log entries  
* `timeago()`      : render relative times in HTML reports  
* `strftime`       : custom date formatting for CSV headers  
* `to_json`        : output nested objects in JSON columns  
* `from_json`      : read JSON blobs from database  
* `to_yaml`        : create YAML config snippets in report  
* `from_yaml`      : parse embedded YAML test cases  
* `render_stream`  : stream huge result sets without loading all at once  
* `extends`        : reuse common report layouts  
* `block`          : override specific sections (charts, tables)  
* `cache_template` : speed up repeated report generation  
* `trans`          : mark UI labels for translation  
* `gettext`        : hook into enterprise localization pipelines  
* `auto_reload`    : live-reload templates as I tweak layouts  
* `if` / `elif` / `else` : conditional sections based on data volume  
* `for` / `endfor`        : loop over rows or grouped categories  
* `syntax_highlight` : get clear error output in my terminal or IDE  

# The Task

I am a localization specialist who needs to produce multi-language email templates, web snippets and PDF blocks. I want to mark strings for translation, pull in dynamic date and number formats, and generate locale-specific JSON and YAML config files. I need smooth integration with gettext, live preview of changed translations, and the ability to stream large catalogs for proofreading. This repo covers all my templating and i18n needs.

# The Requirements

* `add`            : adjust numeric formats in-template (e.g. 1.234 + 0.007)  
* `sub`            : modify values for locale rules  
* `mul`            : apply multipliers for regional units  
* `div`            : divide for ratio-based formatting  
* `is_even`        : helper for table row styling  
* `is_odd`         : helper for alternating backgrounds  
* `date(format)`   : locale-aware date formatting  
* `timeago()`      : render time differences in target language  
* `strftime`       : custom pattern for local conventions  
* `to_json`        : export localized data as JSON  
* `from_json`      : import fallback strings  
* `to_yaml`        : output locale bundles in YAML  
* `from_yaml`      : read translation source files  
* `render_stream`  : stream large translation previews  
* `extends`        : share common layout across locales  
* `block`          : override only text sections per locale  
* `cache_template` : speed up repeated preview renders  
* `trans`          : wrap translatable text segments  
* `gettext`        : hook directly into .po/.mo pipelines  
* `auto_reload`    : live-reload when .po or template changes  
* `if` / `elif` / `else` : conditional content by region or plural rules  
* `for` / `endfor`        : iterate through translation keys  
* `syntax_highlight` : colored diffs and error annotations for translators  

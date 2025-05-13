# The Task

I am a Localization Manager. I want to streamline the translation of CLI tools, generate localized docs, and verify workflows in multiple languages. This code repository helps me manage i18n/l10n, export bilingual documentation, and integrate translated prompts into CI tests.

# The Requirements

* `set_renderer`           : Output help text and prompts in colorized table format, plain text, JSON for TMS, or Markdown.  
* `pipe`                   : Feed untranslated resource files into translation-checkers and back into the workflow automatically.  
* `parallelize`            : Run locale validation, terminology checks, and QA steps in parallel.  
* `secure_input`           : Manage API keys for translation services with masked prompts and secure cleanup.  
* `translate`              : Load and apply translations for help text, error messages, and prompts into multiple languages.  
* `export_workflow`        : Export the end-to-end localization workflow as Markdown or HTML guides.  
* `load_config`            : Read locale-specific settings and glossaries from JSON, YAML, TOML, or INI.  
* `env_inject`             : Map environment variables (LOCALE, TRANSLATOR_API_URL) to command parameters.  
* `load_plugins`           : Discover and load external format converters or glossary validators as plugins.  
* `redirect_io`            : Redirect translation QA reports and logs to files or custom review systems.  

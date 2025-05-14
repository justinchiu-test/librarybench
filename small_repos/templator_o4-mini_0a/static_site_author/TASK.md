# The Task

I am a static site author creating a personal blog and documentation site. I want rapid rebuilds, template components for posts and layouts, and full control over escaping and whitespace. This repository is my static-site engine foundation.

# The Requirements

* `auto_reload`           : Watch markdown and template files; automatically recompile on change.  
* `define_macro`          : Use macros for navbars, footers, and code block wrappers.  
* `precompile_templates`  : Generate standalone Python modules for templates to speed up the build process.  
* `set_output_mode`       : Html-escape by default; switch to raw mode when embedding third-party scripts.  
* `url_encode`            : Encode permalinks and asset URLs.  
* `url_decode`            : Decode legacy URLs for redirects.  
* `querystring`           : Construct tag archive links with pagination parameters.  
* `to_json`               : Embed site metadata and search indices in JSON.  
* `from_json`             : Load JSON snippets to drive pagination or gallery layouts.  
* `to_yaml`               : Output frontmatter or config sections in YAML within pages.  
* `from_yaml`             : Parse YAML frontmatter directly inside templates.  
* `trim_whitespace`       : Precision-control markup spacing, especially around lists and code fences.  
* `render_threadsafe`     : Allow multiple build threads to render pages in parallel safely.  
* `render_async`          : Stream partial pages or use async data loaders for RSS feeds.  
* `set_locale`            : Generate multilingual site builds (`en`, `es`, `de`).  
* `trans`                 : Wrap translatable strings in templates for later extraction.  
* `render_to_string`      : Generate HTML strings for in-memory indexing.  
* `render_to_file`        : Write final `.html` files out to the `dist/` folder.  

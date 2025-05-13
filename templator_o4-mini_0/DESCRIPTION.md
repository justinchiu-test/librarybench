# Templator

## Purpose and Motivation
Templator is a minimalist text-templating engine supporting variable interpolation, loops, and conditionals. It keeps its footprint small by relying only on the standard library (e.g., `re` and `ast`). You can render configuration files, HTML snippets, reports, or code templates with a clear syntax. Extension points let you inject custom filters or tag handlers to suit specialized DSLs.

## Core Functionality
- Parse templates with delimiters for variables (`{{ var }}`) and control blocks (`{% if %}`, `{% for %}`)  
- Rendering context with scoped namespaces and safe evaluation (using `ast.literal_eval` for expressions)  
- Built-in filters (upper, lower, length, default) and plugin API for custom filters  
- Error reporting with source snippet and line numbers  
- Render to string or write directly to a target file  
- Auto-escaping or raw output modes for safe generation  


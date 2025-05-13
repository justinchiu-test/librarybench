# TemplateX

## Purpose and Motivation
TemplateX is a minimal templating engine that extends Python’s built-in string and re modules to offer placeholder substitution, conditional blocks, and loops. It fills the gap between basic `str.format` and full-blown templating frameworks, with zero external dependencies. TemplateX is ideal for generating code, configuration files, or simple HTML reports in lightweight scripts.

## Core Functionality
- Define templates with delimiters for variable substitution, conditionals (`if/else`), and loops (`for item in list`)  
- Namespace-based context injection with dot-notation access to nested data  
- Custom filter functions that transform values during rendering  
- Built-in escaping modes for HTML, JSON, or shell scripts  
- Template inheritance or partials (include other templates)  
- Ability to precompile templates to AST-like structures for faster repeated rendering  


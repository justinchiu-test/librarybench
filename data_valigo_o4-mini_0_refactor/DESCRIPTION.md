# data_valigo

## Purpose and Motivation
data_valigo is a rule‐based data validation and transformation toolkit for Python. It streamlines the process of declaring schemas, applying type checks, normalizing values, and aggregating errors—all using only built-in modules like `re`, `datetime`, and `decimal`. Useful for form processing, CSV/JSON ingestion, and API input validation in lightweight services.

## Core Functionality
- Define validation rules for common data types (strings, numbers, dates, emails)  
- Compose rules into field schemas and enforce required/optional constraints  
- Automatic cleaning/transformation (trimming, case normalization, type casting)  
- Bulk validation with aggregated error reporting  
- Custom rule injection (user-supplied callables)  
- Import/export schemas in JSON‐like dictionaries for dynamic use  


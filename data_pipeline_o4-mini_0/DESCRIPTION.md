# DataPipeline

## Purpose and Motivation
DataPipeline makes it easy to build in-memory, functional or object-oriented ETL pipelines using built-in Python data structures and modules (like `itertools`, `functools`). It’s ideal for processing CSV/text data, transforming records, and loading results without heavyweight frameworks.

## Core Functionality
- Define named pipeline stages that accept and yield row or record iterators  
- Built-in stage functions: filtering, mapping, batching, sorting, grouping  
- Compose pipelines via a simple declarative API or a fluent builder pattern  
- Support error-handling strategies (skip, retry, fallback) within stages  
- Ability to serialize pipeline definitions to JSON/YAML for introspection  
- Hooks for custom source/sink connectors (e.g., reading from files, writing to sockets)  

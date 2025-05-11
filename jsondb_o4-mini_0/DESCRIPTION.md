# JSONDB

## Purpose and Motivation
JSONDB provides a lightweight, file-backed document store with JSON persistence and in-memory indexing. It lets you treat a directory of JSON files as a mini database, supporting insert, update, delete and query operations without external dependencies. Developers can rapidly prototype data-driven applications without installing a full database engine. This abstraction simplifies common patterns of document management, safe commits, and simple indexing for faster lookups.

## Core Functionality
- Insert, update, delete and batch upsert JSON documents with unique identifiers  
- Query engine supporting field‐based filters, nested‐attribute lookups, and simple operators (`==`, `<`, `in`, etc.)  
- In‐memory index management (single‐field and compound indexes) that replays on load and updates on write  
- Safe file‐based persistence (atomic writes via temp-files and rename, optional journaling for rollback)  
- Transaction‐style batch operations with commit/rollback semantics  
- Hooks for validation, transformation, and change callbacks  


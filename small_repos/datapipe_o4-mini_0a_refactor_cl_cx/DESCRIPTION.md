# DataPipe

## Purpose and Motivation
DataPipe provides a modular ETL (Extract–Transform–Load) pipeline framework using only built-in modules. It makes it easy to wire together data sources, transformation steps, and sinks, allowing fine-grained error handling and metrics collection. Use DataPipe for CSV-to-JSON conversions, in-memory data filtering, or even streaming logs through multiple processors.

## Core Functionality
- Define pipeline stages as functions or class-based processors with a common interface  
- Chain sources, transforms, and sinks into declarative pipelines  
- Batch or streaming execution modes, with backpressure control  
- Built-in adapters for file I/O (CSV, JSON), in-memory queues, and HTTP endpoints (using urllib)  
- Error handling strategies: skip, retry, halt, or route to dead-letter stage  
- Metrics collection via simple counters and timers, with optional console reporting  


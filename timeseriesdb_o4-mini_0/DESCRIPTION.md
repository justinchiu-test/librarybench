# TimeSeriesDB

## Purpose and Motivation
TimeSeriesDB is an in-memory, tag-aware time series aggregator and query engine. It ingests timestamped records and lets you perform range queries, downsampling, and rolling aggregations—all using standard Python containers. It’s ideal for prototyping monitoring tools, analytics pipelines, or event-stream summarization without a heavy TSDB install.

## Core Functionality
- Append data points (`timestamp`, `tags`, `value`) into named series  
- Range queries with optional tag filters (exact match or partial)  
- Aggregation functions (sum, avg, min, max, count) over arbitrary intervals  
- Downsampling/down-aggregation (bucket by fixed window sizes) and retention policies  
- Export/import of series in CSV or JSON formats  
- Hooks for custom aggregators and on-the-fly data transformation  


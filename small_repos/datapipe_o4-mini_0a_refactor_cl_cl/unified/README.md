# DataPipe

A modular ETL (Extract–Transform–Load) pipeline framework using only built-in Python modules. It makes it easy to wire together data sources, transformation steps, and sinks, allowing fine-grained error handling and metrics collection.

## Installation

```bash
pip install .
```

## Features

- **Pipeline Construction**: Define stages as functions or class-based processors
- **Windowing Operations**:
  - `tumbling_window()`: Group data into non-overlapping fixed-size windows
  - `sliding_window()`: Compute metrics over overlapping windows
- **Serialization**:
  - `add_serializer()`: Register custom serializers (JSON, Avro, Parquet)
  - `get_serializer()`: Retrieve registered serializers
- **Flow Control**:
  - `throttle_upstream()`: Apply backpressure to manage overloaded stages
  - `watermark_event_time()`: Handle late-arriving data correctly
- **Error Handling**:
  - `halt_on_error()`: Stop pipeline on any error
  - `skip_error()`: Continue processing despite errors
- **Operations**:
  - `setup_logging()`: Configure logging for the pipeline
  - `cli_manage()`: Command-line interface for pipelines
  - `parallelize_stages()`: Run stages in parallel for improved throughput
  - `track_lineage()`: Track data lineage for auditing

## Example Usage

```python
from datapipe import tumbling_window, skip_error, parallelize_stages

# Process data in windows
records = [{'timestamp': i, 'value': i*2} for i in range(10)]
windows = tumbling_window(records, window_size=3)

# Error handling decorator
@skip_error
def process_data(record):
    return record['value'] / record.get('divisor', 1)

# Parallel processing
def extract(data):
    return [item['value'] for item in data]

def transform(data):
    return [item * 2 for item in data]

def load(data):
    return {'loaded': data}

stages = {'extract': extract, 'transform': transform, 'load': load}
results = parallelize_stages(stages, records)
```

## Use Cases

- CSV-to-JSON conversions
- In-memory data filtering
- Streaming logs through multiple processors
- Real-time data analysis
- ETL pipeline construction
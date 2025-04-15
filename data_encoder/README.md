# Data Encoder

A binary serialization library that can encode and decode Python data types into a compact format for storage or transmission.

## Features

### Basic Types
- Encode and decode primitive data types:
  - Integers
  - Strings
  - Booleans

### Collections
- Homogeneous lists (lists where all elements are of the same type)
- Homogeneous sets (sets where all elements are of the same type)
- Dictionaries with string keys and mixed value types

### Advanced Features
- Nested collections (e.g., lists of lists, dictionaries with list values)
- Schema-based encoding for structured data
- Field-level access for schema-encoded data
- Optional compression for efficiency

## Binary Format

The binary format is designed to be compact and simple:

1. **Type Headers (1 byte)**:
   - `0x01`: Integer
   - `0x02`: String
   - `0x03`: Boolean
   - `0x04`: List
   - `0x05`: Set
   - `0x06`: Dictionary
   - `0x07`: Schema-based object
   - `0x08`: Compressed data wrapper

2. **Data Structure**:
   - **Integer**: `INTEGER_TYPE (1 byte) + Size (4 bytes) + Value Bytes`
   - **String**: `STRING_TYPE (1 byte) + Length (4 bytes) + UTF-8 Bytes`
   - **Boolean**: `BOOLEAN_TYPE (1 byte) + Value (1 byte, 0 or 1)`
   - **List**: `LIST_TYPE (1 byte) + Length (4 bytes) + Item Type (1 byte) + Items`
   - **Set**: `SET_TYPE (1 byte) + Length (4 bytes) + Item Type (1 byte) + Items`
   - **Dictionary**: `DICT_TYPE (1 byte) + Count (4 bytes) + (Key-Value Pairs)*`
   - **Schema**: `SCHEMA_TYPE (1 byte) + Schema Definition + Field Positions + Data`
   - **Compressed**: `COMPRESSED_TYPE (1 byte) + Original Size (4 bytes) + Compressed Data`

## Usage

### Basic Usage

```python
from data_encoder import encode, decode

# Encoding and decoding primitives
encoded_int = encode(42)
decoded_int = decode(encoded_int)  # 42

encoded_str = encode("Hello, World!")
decoded_str = decode(encoded_str)  # "Hello, World!"

encoded_bool = encode(True)
decoded_bool = decode(encoded_bool)  # True

# Encoding and decoding collections
encoded_list = encode([1, 2, 3])
decoded_list = decode(encoded_list)  # [1, 2, 3]

encoded_set = encode({1, 2, 3})
decoded_set = decode(encoded_set)  # {1, 2, 3}

encoded_dict = encode({"name": "Alice", "age": 30, "active": True})
decoded_dict = decode(encoded_dict)  # {"name": "Alice", "age": 30, "active": True}
```

### Schema-Based Encoding

```python
from data_encoder import encode, decode

# Define a schema
schema = {
    "name": "str",
    "age": "int",
    "scores": ["int"]  # List of integers
}

# Create data that matches the schema
data = {
    "name": "Alice",
    "age": 30,
    "scores": [85, 90, 95]
}

# Encode with schema
encoded = encode(data, schema=schema)

# Decode the entire object
decoded = decode(encoded)
print(decoded)  # {"name": "Alice", "age": 30, "scores": [85, 90, 95]}

# Or access just one field efficiently
name = decode(encoded, field="name")
print(name)  # "Alice"
```

### Compression with Multiple Algorithms

```python
from data_encoder import encode, decode

# Large data
large_string = "a" * 10000

# Encode with compression using different algorithms
encoded_zlib = encode(large_string, compress=True, compression_algorithm="zlib")  # Default
encoded_gzip = encode(large_string, compress=True, compression_algorithm="gzip")
encoded_lzma = encode(large_string, compress=True, compression_algorithm="lzma")

# Compare compression ratios
print(f"Original size: {len(large_string)} bytes")
print(f"zlib size: {len(encoded_zlib)} bytes")
print(f"gzip size: {len(encoded_gzip)} bytes")
print(f"lzma size: {len(encoded_lzma)} bytes")

# Decoding works the same way regardless of algorithm used
decoded = decode(encoded_lzma)
print(len(decoded))  # 10000

# Compression strengths vary by data type and size:
# - zlib: Fast general-purpose compression
# - gzip: Similar to zlib but with extra headers, good for files
# - lzma: Better compression for large files, but slower
```

## Running Tests

```bash
pytest tests.py
```
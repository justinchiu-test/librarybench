#!/usr/bin/env python
"""
Example usage of the data_encoder library.
"""

from data_encoder import encode, decode
import sys
import time

def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}\n")

def basic_examples():
    """Demonstrate basic encoding and decoding."""
    print_section("Basic Examples")

    # Integer
    encoded_int = encode(42)
    decoded_int = decode(encoded_int)
    print(f"Integer: {decoded_int} (encoded size: {len(encoded_int)} bytes)")

    # String
    encoded_str = encode("Hello, World!")
    decoded_str = decode(encoded_str)
    print(f"String: {decoded_str} (encoded size: {len(encoded_str)} bytes)")
    
    # Boolean
    encoded_bool = encode(True)
    decoded_bool = decode(encoded_bool)
    print(f"Boolean: {decoded_bool} (encoded size: {len(encoded_bool)} bytes)")
    
    # List
    encoded_list = encode([1, 2, 3, 4, 5])
    decoded_list = decode(encoded_list)
    print(f"List: {decoded_list} (encoded size: {len(encoded_list)} bytes)")
    
    # Set
    encoded_set = encode({1, 2, 3, 4, 5})
    decoded_set = decode(encoded_set)
    print(f"Set: {decoded_set} (encoded size: {len(encoded_set)} bytes)")
    
    # Dictionary
    data = {"name": "Alice", "age": 30, "active": True}
    encoded_dict = encode(data)
    decoded_dict = decode(encoded_dict)
    print(f"Dictionary: {decoded_dict} (encoded size: {len(encoded_dict)} bytes)")

def compression_example():
    """Demonstrate different compression algorithms."""
    print_section("Compression Algorithms Comparison")
    
    # Create some repetitive data that should compress well
    large_data = "a" * 1000 + "b" * 1000 + "c" * 1000
    
    # Encode without compression
    start = time.time()
    encoded_normal = encode(large_data)
    normal_time = time.time() - start
    
    print(f"Original data length: {len(large_data)} characters")
    print(f"Encoded size (without compression): {len(encoded_normal)} bytes")
    
    # Test all compression algorithms
    algorithms = ["zlib", "gzip", "lzma"]
    
    print("\nCompression algorithm comparison:")
    print("-" * 60)
    print(f"{'Algorithm':<10} {'Size (bytes)':<15} {'Ratio':<10} {'Time (sec)':<15} {'Verified':<10}")
    print("-" * 60)
    
    for algorithm in algorithms:
        # Encode with this algorithm
        start = time.time()
        encoded = encode(large_data, compress=True, compression_algorithm=algorithm)
        algorithm_time = time.time() - start
        
        # Calculate compression ratio
        ratio = len(encoded_normal) / len(encoded)
        
        # Verify decoded data is the same
        decoded = decode(encoded)
        verified = "✓" if decoded == large_data else "✗"
        
        # Print results
        print(f"{algorithm:<10} {len(encoded):<15} {ratio:<10.2f}x {algorithm_time:<15.6f} {verified:<10}")
    
    # Try with a different type of data - JSON-like structure
    print("\nCompressing structured data:")
    complex_data = {
        "users": [
            {"name": "Alice", "age": 30, "active": True, "scores": [90, 85, 95]},
            {"name": "Bob", "age": 25, "active": False, "scores": [70, 65, 80]},
            {"name": "Charlie", "age": 35, "active": True, "scores": [85, 90, 80]},
        ] * 10,  # Duplicate to make larger
        "settings": {
            "version": "1.0.0",
            "theme": "dark",
            "notifications": True,
            "language": "en-US",
            "timezone": "UTC-5",
            "features": ["search", "export", "import", "sharing"],
        }
    }
    
    encoded_normal = encode(complex_data)
    print(f"\nComplex data encoded size: {len(encoded_normal)} bytes")
    print("-" * 60)
    print(f"{'Algorithm':<10} {'Size (bytes)':<15} {'Ratio':<10}")
    print("-" * 60)
    
    for algorithm in algorithms:
        encoded = encode(complex_data, compress=True, compression_algorithm=algorithm)
        ratio = len(encoded_normal) / len(encoded)
        print(f"{algorithm:<10} {len(encoded):<15} {ratio:<10.2f}x")
    
    print("\nCompression Notes:")
    print("- zlib: Fast general-purpose compression")
    print("- gzip: Similar to zlib but with file headers, good for files")
    print("- lzma: Better for larger files, higher compression but slower")

def schema_example():
    """Demonstrate schema-based encoding."""
    print_section("Schema-Based Encoding")
    
    # Define a schema for a person record
    schema = {
        "name": "str",
        "age": "int",
        "active": "bool",
        "scores": ["int"],  # list of integers
        "tags": ["str"]     # list of strings
    }
    
    # Create some sample data
    data = {
        "name": "Bob Smith",
        "age": 42,
        "active": True,
        "scores": [85, 90, 78, 92],
        "tags": ["developer", "python", "data"]
    }
    
    # Encode with schema
    encoded = encode(data, schema=schema)
    
    # Decode the entire object
    decoded = decode(encoded)
    print(f"Full decoded data: {decoded}")
    print(f"Encoded size: {len(encoded)} bytes")
    
    # Access individual fields
    print("\nField-level access:")
    print(f"  Name: {decode(encoded, field='name')}")
    print(f"  Age: {decode(encoded, field='age')}")
    print(f"  Scores: {decode(encoded, field='scores')}")
    
    # Demonstrate missing field (uses default value)
    partial_data = {
        "name": "Charlie Brown",
        "active": False,
        "scores": [70, 75, 80],
        "tags": ["student"]
    }
    
    encoded_partial = encode(partial_data, schema=schema)
    decoded_partial = decode(encoded_partial)
    print("\nPartial data with defaults:")
    print(f"  {decoded_partial}")
    print(f"  Note that 'age' defaulted to {decoded_partial['age']}")

def nested_structure_example():
    """Demonstrate encoding of complex nested structures."""
    print_section("Complex Nested Structures")
    
    # Create a complex nested data structure
    data = {
        "users": [
            {
                "name": "Alice",
                "permissions": {"read": True, "write": False},
                "groups": ["admin", "users"]
            },
            {
                "name": "Bob",
                "permissions": {"read": True, "write": True},
                "groups": ["users"]
            }
        ],
        "settings": {
            "active": True,
            "theme": "dark",
            "notifications": ["email", "sms"]
        }
    }
    
    # Encode and decode
    encoded = encode(data)
    decoded = decode(encoded)
    
    # Pretty print the result
    import json
    print(f"Complex structure encoded size: {len(encoded)} bytes")
    print("Decoded structure:")
    print(json.dumps(decoded, indent=2))
    
    # Show compression benefit for complex structures
    encoded_compressed = encode(data, compress=True)
    print(f"\nCompressed size: {len(encoded_compressed)} bytes")
    print(f"Compression ratio: {len(encoded) / len(encoded_compressed):.2f}x")

def main():
    """Run all examples."""
    print("Data Encoder Examples")
    print("---------------------")
    
    basic_examples()
    compression_example()
    schema_example()
    nested_structure_example()

if __name__ == "__main__":
    main()
import unittest
import sys
import zlib
from data_encoder import encode, decode, _encode_with_schema

class TestDataEncoder(unittest.TestCase):
    def test_encode_decode_integers(self):
        # Test small integers
        self.assertEqual(decode(encode(0)), 0)
        self.assertEqual(decode(encode(42)), 42)
        self.assertEqual(decode(encode(-10)), -10)
        
        # Test large integers
        self.assertEqual(decode(encode(999999)), 999999)
        self.assertEqual(decode(encode(-999999)), -999999)
    
    def test_encode_decode_strings(self):
        # Test empty string
        self.assertEqual(decode(encode("")), "")
        
        # Test ASCII strings
        self.assertEqual(decode(encode("hello")), "hello")
        self.assertEqual(decode(encode("Hello, World!")), "Hello, World!")
        
        # Test Unicode strings
        self.assertEqual(decode(encode("你好")), "你好")
        self.assertEqual(decode(encode("🚀✨")), "🚀✨")
    
    def test_encode_decode_booleans(self):
        self.assertEqual(decode(encode(True)), True)
        self.assertEqual(decode(encode(False)), False)
    
    def test_encode_decode_homogeneous_lists(self):
        # Test empty list
        self.assertEqual(decode(encode([])), [])
        
        # Test integer lists
        self.assertEqual(decode(encode([1, 2, 3])), [1, 2, 3])
        self.assertEqual(decode(encode([-10, 0, 10])), [-10, 0, 10])
        
        # Test string lists
        self.assertEqual(decode(encode(["a", "b", "c"])), ["a", "b", "c"])
        self.assertEqual(decode(encode(["hello", "world"])), ["hello", "world"])
        
        # Test boolean lists
        self.assertEqual(decode(encode([True, False, True])), [True, False, True])
        
        # Test nested lists
        self.assertEqual(decode(encode([[1, 2], [3, 4]])), [[1, 2], [3, 4]])
    
    def test_encode_decode_sets(self):
        # Test empty set
        self.assertEqual(decode(encode(set())), set())
        
        # Test integer sets
        self.assertEqual(decode(encode({1, 2, 3})), {1, 2, 3})
        self.assertEqual(decode(encode({-10, 0, 10})), {-10, 0, 10})
        
        # Test string sets
        self.assertEqual(decode(encode({"a", "b", "c"})), {"a", "b", "c"})
        self.assertEqual(decode(encode({"hello", "world"})), {"hello", "world"})
        
        # Test boolean sets
        self.assertEqual(decode(encode({True, False})), {True, False})
    
    def test_encode_decode_dictionaries(self):
        # Test empty dictionary
        self.assertEqual(decode(encode({})), {})
        
        # Test simple dictionary
        self.assertEqual(decode(encode({"name": "Alice", "age": 30})), {"name": "Alice", "age": 30})
        
        # Test nested dictionary
        self.assertEqual(
            decode(encode({"user": {"name": "Bob", "active": True}, "scores": [10, 20, 30]})),
            {"user": {"name": "Bob", "active": True}, "scores": [10, 20, 30]}
        )
    
    def test_compression_algorithms(self):
        # Create a test string with lots of repetition for good compression
        test_data = "a" * 5000 + "b" * 5000 + "c" * 5000
        
        # Get uncompressed size
        encoded_uncompressed = encode(test_data, compress=False)
        uncompressed_size = len(encoded_uncompressed)
        
        # Test all compression algorithms
        algorithms = ["zlib", "gzip", "lzma"]
        compressed_sizes = {}
        
        for algorithm in algorithms:
            # Encode with this algorithm
            encoded = encode(test_data, compress=True, compression_algorithm=algorithm)
            compressed_sizes[algorithm] = len(encoded)
            
            # Ensure compression actually reduced size
            self.assertLess(len(encoded), uncompressed_size, 
                           f"{algorithm} compression did not reduce size")
            
            # Ensure we can decode correctly
            decoded = decode(encoded)
            self.assertEqual(decoded, test_data, 
                           f"Decoding failed with {algorithm} compression")
        
        # Test that small strings aren't compressed regardless of algorithm
        small_string = "hello world"
        for algorithm in algorithms:
            encoded_small = encode(small_string, compress=True, compression_algorithm=algorithm)
            # For very small data, compression should be skipped entirely
            self.assertEqual(len(encoded_small), len(encode(small_string, compress=False)),
                            f"{algorithm} tried to compress small data when it shouldn't")
            
        # Print comparison information (optional)
        print(f"\nCompression size comparison for {len(test_data)} bytes of repetitive data:")
        print(f"Uncompressed: {uncompressed_size} bytes")
        for algo, size in compressed_sizes.items():
            ratio = uncompressed_size / size
            print(f"{algo}: {size} bytes ({ratio:.2f}x smaller)")
        
        # Note on compression effectiveness:
        # Different algorithms have different strengths based on data type.
        # Generally:
        # - zlib: Good general-purpose compression, fast
        # - gzip: Similar to zlib but with extra headers, good for files
        # - lzma: Better compression ratios for large files, but slower
        # 
        # For our simple repeated data test, zlib is actually very efficient!
        print("\nCompression algorithm comparison complete.")
    
    def test_schema_encoding(self):
        # Define a schema
        schema = {
            "name": "str",
            "age": "int",
            "scores": ["int"]
        }
        
        # Define data matching the schema
        data = {
            "name": "Alice",
            "age": 30,
            "scores": [85, 90, 95]
        }
        
        # Encode with schema
        encoded = encode(data, schema=schema)
        
        # Decode and verify
        decoded = decode(encoded)
        self.assertEqual(decoded, data)
        
        # Test with missing fields (should use defaults)
        partial_data = {
            "name": "Bob",
            "scores": [70, 75, 80]
        }
        
        encoded_partial = encode(partial_data, schema=schema)
        decoded_partial = decode(encoded_partial)
        
        # Age should default to 0
        self.assertEqual(decoded_partial["age"], 0)
        self.assertEqual(decoded_partial["name"], "Bob")
        self.assertEqual(decoded_partial["scores"], [70, 75, 80])
    
    def test_field_level_access(self):
        # Define a schema with multiple fields
        schema = {
            "name": "str",
            "age": "int",
            "active": "bool",
            "scores": ["int"],
            "address": "dict"
        }
        
        # Define complex data
        data = {
            "name": "Alice Johnson",
            "age": 32,
            "active": True,
            "scores": [88, 92, 95],
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345"
            }
        }
        
        # Encode with schema
        encoded = encode(data, schema=schema)
        
        # Extract individual fields
        name = decode(encoded, field="name")
        age = decode(encoded, field="age")
        active = decode(encoded, field="active")
        scores = decode(encoded, field="scores")
        address = decode(encoded, field="address")
        
        # Verify each field was extracted correctly
        self.assertEqual(name, "Alice Johnson")
        self.assertEqual(age, 32)
        self.assertEqual(active, True)
        self.assertEqual(scores, [88, 92, 95])
        self.assertEqual(address, {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345"
        })
        
        # Test with invalid field name
        with self.assertRaises(ValueError):
            decode(encoded, field="nonexistent")
    
    def test_type_preservation(self):
        # Make sure the original type is preserved
        self.assertIsInstance(decode(encode(42)), int)
        self.assertIsInstance(decode(encode("hello")), str)
        self.assertIsInstance(decode(encode(True)), bool)
        self.assertIsInstance(decode(encode([1, 2, 3])), list)
        self.assertIsInstance(decode(encode({1, 2, 3})), set)
        self.assertIsInstance(decode(encode({"a": 1, "b": 2})), dict)
    
    def test_error_handling(self):
        # Test with invalid binary data
        with self.assertRaises(ValueError):
            decode(b'\x99\x01\x02\x03')  # Invalid type header
        
        # Test with unsupported types
        with self.assertRaises(TypeError):
            encode(complex(1, 2))  # Complex numbers not supported
        
        # Test with non-homogeneous lists
        with self.assertRaises(TypeError):
            encode([1, "string", True])  # Mixed types
        
        # Test with non-homogeneous sets
        with self.assertRaises(TypeError):
            encode({1, "string", True})  # Mixed types
        
        # Test schema validation errors
        schema = {"name": "str", "age": "int"}
        
        # Test with wrong field type
        with self.assertRaises(TypeError):
            encode({"name": 123, "age": 30}, schema=schema)  # name should be string
            
        # Test with non-dictionary data
        with self.assertRaises(TypeError):
            encode("not_a_dict", schema=schema)
    
    def test_complex_nested_structures(self):
        # Test deeply nested structures
        complex_data = {
            "users": [
                {
                    "name": "Alice",
                    "permissions": {"read": True, "write": False},
                    "groups": ["admin", "users"],
                    "scores": {90, 85, 95}
                },
                {
                    "name": "Bob",
                    "permissions": {"read": True, "write": True},
                    "groups": ["users"],
                    "scores": {75, 80, 85}
                }
            ],
            "settings": {
                "active": True,
                "theme": "dark",
                "notifications": ["email", "sms"]
            }
        }
        
        # Encode and decode
        encoded = encode(complex_data)
        decoded = decode(encoded)
        
        # Convert sets to sorted lists for comparison
        # (because order can be different when decoding sets)
        def normalize_sets(obj):
            if isinstance(obj, dict):
                return {k: normalize_sets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [normalize_sets(item) for item in obj]
            elif isinstance(obj, set):
                return sorted(list(obj))
            else:
                return obj
        
        # Compare normalized data
        self.assertEqual(normalize_sets(decoded), normalize_sets(complex_data))
    
    def test_performance_with_large_data(self):
        # Create a large nested structure, but with more reasonable sizes
        large_data = {
            "strings": ["test" * 10 for _ in range(20)],
            "numbers": list(range(100)),
            "nested": [{"key": f"value{i}", "data": [j for j in range(10)]} for i in range(10)]
        }
        
        # Encode and decode without compression
        encoded_normal = encode(large_data)
        decoded_normal = decode(encoded_normal)
        
        # Encode and decode with compression
        encoded_compressed = encode(large_data, compress=True)
        decoded_compressed = decode(encoded_compressed)
        
        # Check that both methods produce identical results
        self.assertEqual(decoded_normal, decoded_compressed)
        
        # Create a large string to test compression effectiveness
        large_string = "a" * 5000
        encoded_str_normal = encode(large_string)
        encoded_str_compressed = encode(large_string, compress=True)
        
        # Check that compression reduced the size for the large string
        self.assertLess(len(encoded_str_compressed), len(encoded_str_normal))
    
    def test_schema_list_type_checking(self):
        # Test schema with list type validation
        schema = {
            "int_list": ["int"],
            "str_list": ["str"],
            "bool_list": ["bool"]
        }
        
        # Valid data
        valid_data = {
            "int_list": [1, 2, 3],
            "str_list": ["a", "b", "c"],
            "bool_list": [True, False, True]
        }
        
        encoded = encode(valid_data, schema=schema)
        decoded = decode(encoded)
        self.assertEqual(decoded, valid_data)
        
        # Invalid data (wrong type in list)
        invalid_data = {
            "int_list": [1, 2, "not an int"],
            "str_list": ["a", "b", "c"],
            "bool_list": [True, False, True]
        }
        
        with self.assertRaises(TypeError):
            encode(invalid_data, schema=schema)


if __name__ == "__main__":
    unittest.main()
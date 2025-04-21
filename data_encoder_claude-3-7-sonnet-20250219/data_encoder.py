from typing import Any, Tuple, Dict, Optional, List, cast, Literal
import zlib
import gzip
import lzma

# Type headers (one byte to identify data type)
INTEGER_TYPE = 0x01
STRING_TYPE = 0x02
BOOLEAN_TYPE = 0x03
LIST_TYPE = 0x04
SET_TYPE = 0x05
DICT_TYPE = 0x06
SCHEMA_TYPE = 0x07
COMPRESSED_TYPE = 0x08  # Used as a wrapper around compressed data

# Compression algorithm identifiers (stored as the first byte after COMPRESSED_TYPE)
ZLIB_COMPRESSION = 0x01
GZIP_COMPRESSION = 0x02
LZMA_COMPRESSION = 0x03

# Compression algorithm type
CompressionAlgorithm = Literal["zlib", "gzip", "lzma"]

# Compression functions
def _compress_zlib(data: bytes) -> bytes:
    """Compress data using zlib."""
    return zlib.compress(data)

def _compress_gzip(data: bytes) -> bytes:
    """Compress data using gzip."""
    return gzip.compress(data)

def _compress_lzma(data: bytes) -> bytes:
    """Compress data using lzma."""
    return lzma.compress(data)

# Decompression functions
def _decompress_zlib(data: bytes) -> bytes:
    """Decompress data using zlib."""
    return zlib.decompress(data)

def _decompress_gzip(data: bytes) -> bytes:
    """Decompress data using gzip."""
    return gzip.decompress(data)

def _decompress_lzma(data: bytes) -> bytes:
    """Decompress data using lzma."""
    return lzma.decompress(data)

# Mapping of algorithm names to functions and type identifiers
COMPRESSION_FUNCTIONS = {
    "zlib": (_compress_zlib, _decompress_zlib, ZLIB_COMPRESSION),
    "gzip": (_compress_gzip, _decompress_gzip, GZIP_COMPRESSION),
    "lzma": (_compress_lzma, _decompress_lzma, LZMA_COMPRESSION),
}

# Default compression algorithm
DEFAULT_COMPRESSION_ALGORITHM: CompressionAlgorithm = "zlib"

# Type mapping for schema validation
TYPE_MAPPING = {
    "int": INTEGER_TYPE,
    "str": STRING_TYPE,
    "bool": BOOLEAN_TYPE,
    "list": LIST_TYPE,
    "set": SET_TYPE,
    "dict": DICT_TYPE,
}

# Reverse mapping for decoding
TYPE_NAME_MAPPING = {v: k for k, v in TYPE_MAPPING.items()}


def _maybe_compress(
    data: bytes, 
    compress: bool, 
    threshold: int,
    algorithm: CompressionAlgorithm = DEFAULT_COMPRESSION_ALGORITHM
) -> bytes:
    """
    Apply compression if enabled and beneficial.
    
    Args:
        data: The data to possibly compress
        compress: Whether compression is enabled
        threshold: Minimum size in bytes before compression is applied
        algorithm: Compression algorithm to use ('zlib', 'gzip', or 'lzma')
        
    Returns:
        The compressed data if compression was applied, otherwise the original data
    """
    if not compress or len(data) < threshold:
        return data
    
    # Get compression function and algorithm ID
    compress_func, _, algo_id = COMPRESSION_FUNCTIONS[algorithm]
    
    # Apply compression
    compressed = compress_func(data)
    
    # Only use compression if it actually makes the data smaller
    if len(compressed) < len(data):
        return (
            bytes([COMPRESSED_TYPE])
            + bytes([algo_id])
            + len(data).to_bytes(4, byteorder="big")
            + compressed
        )
    
    return data


def encode(
    data: Any,
    schema: Optional[Dict[str, Any]] = None,
    compress: bool = False,
    compression_threshold: int = 1024,
    compression_algorithm: CompressionAlgorithm = DEFAULT_COMPRESSION_ALGORITHM,
) -> bytes:
    """
    Encode a Python object into a binary format.

    Supported types:
    - int: INTEGER_TYPE + size (4 bytes) + value
    - str: STRING_TYPE + length (4 bytes) + UTF-8 bytes
    - bool: BOOLEAN_TYPE + 1 byte (0 or 1)
    - list (homogeneous): LIST_TYPE + length (4 bytes) + item type (1 byte) + items
    - set (homogeneous): SET_TYPE + length (4 bytes) + item type (1 byte) + items
    - dict: DICT_TYPE + length (4 bytes) + key-value pairs
    - schema-based object: SCHEMA_TYPE + schema encoding + values

    Args:
        data: The data to encode
        schema: Optional schema definition for structured data
        compress: Whether to compress data when beneficial
        compression_threshold: Minimum size in bytes before compression is applied
        compression_algorithm: Algorithm to use for compression ('zlib', 'gzip', or 'lzma')

    Returns:
        bytes: The encoded data

    Raises:
        TypeError: If the data type is not supported
    """
    # If schema is provided, encode according to schema
    if schema is not None:
        return _encode_with_schema(
            data,
            schema, 
            compress, 
            compression_threshold,
            compression_algorithm
        )

    # Handle each supported type
    if isinstance(data, bool):
        # For booleans, we store a type byte and a single byte (0 or 1)
        # Handle boolean case first since bool is a subclass of int
        result = bytes([BOOLEAN_TYPE]) + bytes([1 if data else 0])
        return _maybe_compress(result, compress, compression_threshold, compression_algorithm)

    elif isinstance(data, int):
        # For integers, we store a type byte, 4 bytes for size, and the value
        value_bytes = data.to_bytes(
            length=(data.bit_length() + 7) // 8 or 1, byteorder="big", signed=True
        )
        size = len(value_bytes)
        result = bytes([INTEGER_TYPE]) + size.to_bytes(4, byteorder="big") + value_bytes
        return _maybe_compress(result, compress, compression_threshold, compression_algorithm)

    elif isinstance(data, str):
        # For strings, we store a type byte, 4 bytes for length, and UTF-8 encoded string
        value_bytes = data.encode("utf-8")
        length = len(value_bytes)
        result = (
            bytes([STRING_TYPE]) + length.to_bytes(4, byteorder="big") + value_bytes
        )
        return _maybe_compress(result, compress, compression_threshold, compression_algorithm)

    elif isinstance(data, list):
        # For lists, we need the length, the type of items, and all encoded items
        if not data:
            # Empty list - we'll set a dummy item type of INTEGER
            result = (
                bytes([LIST_TYPE])
                + (0).to_bytes(4, byteorder="big")
                + bytes([INTEGER_TYPE])
            )
            return _maybe_compress(result, compress, compression_threshold, compression_algorithm)

        # Check if all elements have the same type
        first_type = type(data[0])
        if not all(isinstance(item, first_type) for item in data):
            raise TypeError("All items in the list must have the same type")

        # Encode each item
        encoded_items = [
            encode(
                item, 
                compress=compress, 
                compression_threshold=compression_threshold,
                compression_algorithm=compression_algorithm
            )
            for item in data
        ]

        # Get the item type from the first encoded item
        # If the first item is compressed, we need to look at its wrapped type
        if encoded_items[0][0] == COMPRESSED_TYPE:
            # Skip the compression header (5 bytes) and get the actual type
            item_type = encoded_items[0][5]
        else:
            item_type = encoded_items[0][0]

        # Build the result: type + length + item type + concatenated items
        length = len(data)
        result = (
            bytes([LIST_TYPE])
            + length.to_bytes(4, byteorder="big")
            + bytes([item_type])
        )

        # For list of primitives, we don't need the type header for each item
        if item_type in (INTEGER_TYPE, STRING_TYPE, BOOLEAN_TYPE):
            for encoded_item in encoded_items:
                # If item is compressed, we need to include the whole item
                if encoded_item[0] == COMPRESSED_TYPE:
                    result += encoded_item
                else:
                    # Skip the type byte since we already included it once
                    result += encoded_item[1:]
        else:
            # For nested structures, include the full encoded items
            for encoded_item in encoded_items:
                result += encoded_item

        return _maybe_compress(result, compress, compression_threshold, compression_algorithm)

    elif isinstance(data, set):
        # Sets are similar to lists but with a different type header
        if not data:
            # Empty set - we'll set a dummy item type of INTEGER
            result = (
                bytes([SET_TYPE])
                + (0).to_bytes(4, byteorder="big")
                + bytes([INTEGER_TYPE])
            )
            return _maybe_compress(result, compress, compression_threshold, compression_algorithm)

        # Convert to list for processing (sets are unordered but we need to process them)
        data_list = list(data)

        # Check if all elements have the same type
        first_type = type(data_list[0])
        if not all(isinstance(item, first_type) for item in data_list):
            raise TypeError("All items in the set must have the same type")

        # Encode each item
        encoded_items = [
            encode(
                item, 
                compress=compress, 
                compression_threshold=compression_threshold,
                compression_algorithm=compression_algorithm
            )
            for item in data_list
        ]

        # Get the item type from the first encoded item
        if encoded_items[0][0] == COMPRESSED_TYPE:
            # Skip the compression header (5 bytes) and get the actual type
            item_type = encoded_items[0][5]
        else:
            item_type = encoded_items[0][0]

        # Build the result: type + length + item type + concatenated items
        length = len(data)
        result = (
            bytes([SET_TYPE]) + length.to_bytes(4, byteorder="big") + bytes([item_type])
        )

        # For set of primitives, we don't need the type header for each item
        if item_type in (INTEGER_TYPE, STRING_TYPE, BOOLEAN_TYPE):
            for encoded_item in encoded_items:
                # If item is compressed, we need to include the whole item
                if encoded_item[0] == COMPRESSED_TYPE:
                    result += encoded_item
                else:
                    # Skip the type byte since we already included it once
                    result += encoded_item[1:]
        else:
            # For nested structures, include the full encoded items
            for encoded_item in encoded_items:
                result += encoded_item

        return _maybe_compress(result, compress, compression_threshold, compression_algorithm)

    elif isinstance(data, dict):
        # For dictionaries, store key-value pairs
        # Format: DICT_TYPE + length (4 bytes) + key1 + value1 + key2 + value2 + ...
        length = len(data)
        result = bytes([DICT_TYPE]) + length.to_bytes(4, byteorder="big")

        # Encode each key-value pair
        for key, value in data.items():
            # Keys must be strings
            if not isinstance(key, str):
                raise TypeError("Dictionary keys must be strings")

            # Encode the key
            key_encoded = encode(
                key, compress=compress, compression_threshold=compression_threshold,
                compression_algorithm=compression_algorithm
            )
            result += key_encoded

            # Encode the value
            value_encoded = encode(
                value, compress=compress, compression_threshold=compression_threshold,
                compression_algorithm=compression_algorithm
            )
            result += value_encoded

        return _maybe_compress(result, compress, compression_threshold, compression_algorithm)

    else:
        raise TypeError(f"Type {type(data).__name__} is not supported for encoding")


def _encode_with_schema(
    data: Any,
    schema: Dict[str, Any],
    compress: bool = False,
    compression_threshold: int = 1024,
    compression_algorithm: CompressionAlgorithm = DEFAULT_COMPRESSION_ALGORITHM,
) -> bytes:
    """Encode data according to a user-defined schema."""
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary when using a schema")

    # First, encode the schema itself (as a dict of field name -> type name)
    schema_encoded = encode(
        schema, compress=compress, compression_threshold=compression_threshold,
        compression_algorithm=compression_algorithm
    )

    # Then encode the data according to the schema
    fields_data = bytes()
    field_positions = {}  # Store positions for field-level access

    # Track position in the encoded data for field-level access
    current_pos = 0

    for field_name, field_type in schema.items():
        if field_name not in data:
            # If a field is missing, use a default value based on the type
            if field_type == "int":
                field_value = 0
            elif field_type == "str":
                field_value = ""
            elif field_type == "bool":
                field_value = False
            elif isinstance(field_type, list) and len(field_type) == 1:
                # List of a specific type
                field_value = []
            elif field_type == "dict":
                field_value = {}
            elif field_type == "set":
                field_value = set()
            else:
                raise ValueError(f"Unsupported type in schema: {field_type}")
        else:
            field_value = data[field_name]

        # Check type compatibility
        if field_type == "int" and not isinstance(field_value, int):
            raise TypeError(f"Field '{field_name}' must be an integer")
        elif field_type == "str" and not isinstance(field_value, str):
            raise TypeError(f"Field '{field_name}' must be a string")
        elif field_type == "bool" and not isinstance(field_value, bool):
            raise TypeError(f"Field '{field_name}' must be a boolean")
        elif isinstance(field_type, list) and not isinstance(field_value, list):
            raise TypeError(f"Field '{field_name}' must be a list")
        elif field_type == "dict" and not isinstance(field_value, dict):
            raise TypeError(f"Field '{field_name}' must be a dictionary")
        elif field_type == "set" and not isinstance(field_value, set):
            raise TypeError(f"Field '{field_name}' must be a set")

        # For list types, ensure homogeneity if a specific type is specified
        if isinstance(field_type, list) and len(field_type) == 1 and field_value:
            inner_type = field_type[0]
            # Cast to list for type checking
            items = cast(List[Any], field_value)
            
            # Skip checks for empty lists
            if inner_type == "int" and not all(
                isinstance(item, int) for item in items
            ):
                raise TypeError(f"All items in '{field_name}' must be integers")
            elif inner_type == "str" and not all(
                isinstance(item, str) for item in items
            ):
                raise TypeError(f"All items in '{field_name}' must be strings")
            elif inner_type == "bool" and not all(
                isinstance(item, bool) for item in items
            ):
                raise TypeError(f"All items in '{field_name}' must be booleans")

        # Store the field's position in the encoded data
        field_positions[field_name] = current_pos

        # Encode the field value
        field_encoded = encode(
            field_value, compress=compress, compression_threshold=compression_threshold,
            compression_algorithm=compression_algorithm
        )
        fields_data += field_encoded

        # Update the position counter
        current_pos += len(field_encoded)

    # Encode the field positions map for field-level access
    positions_encoded = encode(
        field_positions, compress=compress, compression_threshold=compression_threshold,
        compression_algorithm=compression_algorithm
    )

    # Final format: SCHEMA_TYPE + schema + positions_map + fields_data
    result = bytes([SCHEMA_TYPE]) + schema_encoded + positions_encoded + fields_data
    return _maybe_compress(result, compress, compression_threshold, compression_algorithm)


def decode(data: bytes, field: Optional[str] = None) -> Any:
    """
    Decode binary data back into Python objects.

    Args:
        data: The binary data to decode
        field: Optional field name to extract from schema-encoded data

    Returns:
        The decoded Python object (int, str, bool, list, set, dict) or a specific field

    Raises:
        ValueError: If the binary data is invalid
        TypeError: If the encoded type is not supported
    """
    if not data:
        raise ValueError("Empty binary data cannot be decoded")

    # Check if data is compressed
    if data[0] == COMPRESSED_TYPE:
        # Get the compression algorithm ID (1 byte)
        algo_id = data[1]
        
        # Map the algorithm ID to the decompression function
        decompress_func = None
        if algo_id == ZLIB_COMPRESSION:
            decompress_func = _decompress_zlib
        elif algo_id == GZIP_COMPRESSION:
            decompress_func = _decompress_gzip
        elif algo_id == LZMA_COMPRESSION:
            decompress_func = _decompress_lzma
        else:
            raise ValueError(f"Unknown compression algorithm ID: {algo_id}")
        
        # Extract compressed data and the original size for verification
        original_size = int.from_bytes(data[2:6], byteorder="big")
        compressed_data = data[6:]

        # Decompress the data
        decompressed = decompress_func(compressed_data)

        # Verify the size matches what we expect (acts as a checksum)
        if len(decompressed) != original_size:
            raise ValueError("Decompressed data size does not match expected size")

        # Decode the decompressed data
        return decode(decompressed, field)

    # First byte is the type
    type_byte = data[0]

    if type_byte == INTEGER_TYPE:
        # Read size (4 bytes)
        size = int.from_bytes(data[1:5], byteorder="big")
        # Read value
        value = int.from_bytes(data[5 : 5 + size], byteorder="big", signed=True)
        return value

    elif type_byte == STRING_TYPE:
        # Read length (4 bytes)
        length = int.from_bytes(data[1:5], byteorder="big")
        # Read and decode string
        value = data[5 : 5 + length].decode("utf-8")
        return value

    elif type_byte == BOOLEAN_TYPE:
        # Read boolean value (1 byte) and explicitly return a bool
        return True if data[1] == 1 else False

    elif type_byte == LIST_TYPE:
        # Read length (4 bytes)
        length = int.from_bytes(data[1:5], byteorder="big")

        if length == 0:
            return []

        # Read item type (1 byte)
        item_type = data[5]

        # Start reading from position 6 (after type, length, and item type)
        pos = 6
        result = []

        if item_type == INTEGER_TYPE:
            for _ in range(length):
                # Read size (4 bytes)
                size = int.from_bytes(data[pos : pos + 4], byteorder="big")
                pos += 4
                # Read value
                value = int.from_bytes(
                    data[pos : pos + size], byteorder="big", signed=True
                )
                pos += size
                result.append(value)

        elif item_type == STRING_TYPE:
            for _ in range(length):
                # Read string length (4 bytes)
                str_length = int.from_bytes(data[pos : pos + 4], byteorder="big")
                pos += 4
                # Read and decode string
                value = data[pos : pos + str_length].decode("utf-8")
                pos += str_length
                result.append(value)

        elif item_type == BOOLEAN_TYPE:
            for _ in range(length):
                # Read boolean value (1 byte) and explicitly create a bool
                result.append(True if data[pos] == 1 else False)
                pos += 1

        elif item_type == COMPRESSED_TYPE:
            # Lists of compressed items are handled differently
            for _ in range(length):
                # Each item has its own compression header
                original_size = int.from_bytes(data[pos + 1 : pos + 5], byteorder="big")
                compressed_size = len(
                    zlib.compress(b"\x00" * original_size)
                )  # Rough estimate

                # Extract the compressed item
                compressed_item = data[pos : pos + 5 + compressed_size]

                # Decode it recursively
                item = decode(compressed_item)
                result.append(item)

                # Update position
                pos += len(compressed_item)

        elif item_type in (LIST_TYPE, SET_TYPE, DICT_TYPE, SCHEMA_TYPE):
            # Handle nested structures - we need to decode each one completely
            for _ in range(length):
                # Find where this item ends by decoding it
                item_data = data[pos:]
                item, consumed = _decode_with_consumed(item_data)
                result.append(item)
                pos += consumed

        else:
            raise ValueError(f"Invalid item type in list: {item_type}")

        return result

    elif type_byte == SET_TYPE:
        # Read length (4 bytes)
        length = int.from_bytes(data[1:5], byteorder="big")

        if length == 0:
            return set()

        # Read item type (1 byte)
        item_type = data[5]

        # Start reading from position 6 (after type, length, and item type)
        pos = 6
        result = set()

        if item_type == INTEGER_TYPE:
            for _ in range(length):
                # Read size (4 bytes)
                size = int.from_bytes(data[pos : pos + 4], byteorder="big")
                pos += 4
                # Read value
                value = int.from_bytes(
                    data[pos : pos + size], byteorder="big", signed=True
                )
                pos += size
                result.add(value)

        elif item_type == STRING_TYPE:
            for _ in range(length):
                # Read string length (4 bytes)
                str_length = int.from_bytes(data[pos : pos + 4], byteorder="big")
                pos += 4
                # Read and decode string
                value = data[pos : pos + str_length].decode("utf-8")
                pos += str_length
                result.add(value)

        elif item_type == BOOLEAN_TYPE:
            for _ in range(length):
                # Read boolean value (1 byte) and explicitly create a bool
                result.add(True if data[pos] == 1 else False)
                pos += 1

        elif item_type == COMPRESSED_TYPE:
            # Sets of compressed items are handled differently
            for _ in range(length):
                # Each item has its own compression header
                original_size = int.from_bytes(data[pos + 1 : pos + 5], byteorder="big")
                compressed_size = len(
                    zlib.compress(b"\x00" * original_size)
                )  # Rough estimate

                # Extract the compressed item
                compressed_item = data[pos : pos + 5 + compressed_size]

                # Decode it recursively
                item = decode(compressed_item)
                result.add(item)

                # Update position
                pos += len(compressed_item)

        elif item_type in (LIST_TYPE, SET_TYPE, DICT_TYPE, SCHEMA_TYPE):
            # Handle nested structures - we need to decode each one completely
            for _ in range(length):
                # Find where this item ends by decoding it
                item_data = data[pos:]
                item, consumed = _decode_with_consumed(item_data)

                # Skip unhashable types
                if isinstance(item, (list, dict)):
                    # Convert to tuple if list, otherwise keep as is (will raise if added to set)
                    if isinstance(item, list):
                        item = tuple(item)

                result.add(item)
                pos += consumed

        else:
            raise ValueError(f"Invalid item type in set: {item_type}")

        return result

    elif type_byte == DICT_TYPE:
        # Read number of key-value pairs (4 bytes)
        count = int.from_bytes(data[1:5], byteorder="big")

        if count == 0:
            return {}

        # Start reading from position 5 (after type and count)
        pos = 5
        result = {}

        for _ in range(count):
            # Decode key
            key_data = data[pos:]
            key, key_size = _decode_with_consumed(key_data)
            pos += key_size

            # Decode value
            value_data = data[pos:]
            value, value_size = _decode_with_consumed(value_data)
            pos += value_size

            # Add to result
            result[key] = value

        return result

    elif type_byte == SCHEMA_TYPE:
        # First, decode the schema
        schema_data = data[1:]  # Skip the SCHEMA_TYPE byte
        schema, schema_size = _decode_with_consumed(schema_data)

        # Next, decode the field positions map
        positions_data = data[1 + schema_size :]
        field_positions, positions_size = _decode_with_consumed(positions_data)

        # If we're only interested in a specific field, extract it directly
        if field is not None:
            if field not in field_positions:
                raise ValueError(f"Field '{field}' not found in schema")

            # Calculate where the field data starts
            field_pos = field_positions[field]
            field_data_start = 1 + schema_size + positions_size + field_pos

            # Extract and decode just this field
            field_data = data[field_data_start:]
            field_value, _ = _decode_with_consumed(field_data)
            return field_value

        # Otherwise, decode all fields
        fields_data = data[1 + schema_size + positions_size :]
        pos = 0
        result = {}

        for field_name in schema:
            field_data = fields_data[pos:]
            field_value, consumed = _decode_with_consumed(field_data)
            result[field_name] = field_value
            pos += consumed

        return result

    else:
        raise ValueError(f"Invalid type byte: {type_byte}")


def _decode_with_consumed(data: bytes) -> Tuple[Any, int]:
    """
    Helper function that decodes data and returns how many bytes were consumed.
    Used for nested structures.

    Args:
        data: The binary data to decode

    Returns:
        Tuple of (decoded_value, bytes_consumed)
    """
    if not data:
        raise ValueError("Empty binary data cannot be decoded")

    # Check if data is compressed
    if data[0] == COMPRESSED_TYPE:
        # Get the compression algorithm ID (1 byte)
        algo_id = data[1]
        
        # Map the algorithm ID to the decompression function
        decompress_func = None
        if algo_id == ZLIB_COMPRESSION:
            decompress_func = _decompress_zlib
        elif algo_id == GZIP_COMPRESSION:
            decompress_func = _decompress_gzip
        elif algo_id == LZMA_COMPRESSION:
            decompress_func = _decompress_lzma
        else:
            raise ValueError(f"Unknown compression algorithm ID: {algo_id}")
        
        # Extract compressed data (original size is in bytes 2-6 but not needed here)
        # We'll just decompress what we have and check for success
        compressed_data = data[6:]

        # Determine the size of the compressed data
        # Since we don't know exactly how many bytes were used, we need to try decompression
        try:
            decompressed = decompress_func(compressed_data)
            # If successful, we used all the compressed data
            consumed = 6 + len(compressed_data)  # 1 byte type + 1 byte algo + 4 bytes size + compressed data

            # Recursively decode the decompressed data
            value, _ = _decode_with_consumed(decompressed)
            return value, consumed
        except Exception as e:
            # Try with shorter chunks until it works (for zlib only, as it supports partial decompression)
            if algo_id == ZLIB_COMPRESSION:
                for i in range(1, len(compressed_data)):
                    try:
                        decompressed = _decompress_zlib(
                            compressed_data[: len(compressed_data) - i]
                        )
                        consumed = 6 + len(compressed_data) - i
                        value, _ = _decode_with_consumed(decompressed)
                        return value, consumed
                    except zlib.error:
                        continue

            # If all attempts fail, raise an error
            raise ValueError(f"Invalid compressed data: {str(e)}")

    # First byte is the type
    type_byte = data[0]

    if type_byte == INTEGER_TYPE:
        # Read size (4 bytes)
        size = int.from_bytes(data[1:5], byteorder="big")
        # Read value
        value = int.from_bytes(data[5 : 5 + size], byteorder="big", signed=True)
        return value, 5 + size

    elif type_byte == STRING_TYPE:
        # Read length (4 bytes)
        length = int.from_bytes(data[1:5], byteorder="big")
        # Read and decode string
        value = data[5 : 5 + length].decode("utf-8")
        return value, 5 + length

    elif type_byte == BOOLEAN_TYPE:
        # Read boolean value (1 byte) and explicitly use True/False
        return True if data[1] == 1 else False, 2

    elif type_byte == LIST_TYPE:
        # Read length (4 bytes)
        length = int.from_bytes(data[1:5], byteorder="big")

        if length == 0:
            return [], 6  # Type byte + length (4) + item type (1)

        # Read item type (1 byte)
        item_type = data[5]

        # Start reading from position 6 (after type, length, and item type)
        pos = 6
        result = []

        if item_type == INTEGER_TYPE:
            for _ in range(length):
                # Read size (4 bytes)
                size = int.from_bytes(data[pos : pos + 4], byteorder="big")
                pos += 4
                # Read value
                value = int.from_bytes(
                    data[pos : pos + size], byteorder="big", signed=True
                )
                pos += size
                result.append(value)

        elif item_type == STRING_TYPE:
            for _ in range(length):
                # Read string length (4 bytes)
                str_length = int.from_bytes(data[pos : pos + 4], byteorder="big")
                pos += 4
                # Read and decode string
                value = data[pos : pos + str_length].decode("utf-8")
                pos += str_length
                result.append(value)

        elif item_type == BOOLEAN_TYPE:
            for _ in range(length):
                # Read boolean value (1 byte) and explicitly create a bool
                result.append(True if data[pos] == 1 else False)
                pos += 1

        elif item_type == COMPRESSED_TYPE:
            # Lists of compressed items are handled differently
            for _ in range(length):
                # Each item has its own compression header
                # Decode it recursively and track consumed bytes
                item_data = data[pos:]
                item, consumed = _decode_with_consumed(item_data)
                result.append(item)
                pos += consumed

        elif item_type in (LIST_TYPE, SET_TYPE, DICT_TYPE, SCHEMA_TYPE):
            # Handle nested structures - we need to decode each one completely
            for _ in range(length):
                # Find where this item ends by decoding it
                item_data = data[pos:]
                item, consumed = _decode_with_consumed(item_data)
                result.append(item)
                pos += consumed

        else:
            raise ValueError(f"Invalid item type in list: {item_type}")

        return result, pos

    elif type_byte == SET_TYPE:
        # Read length (4 bytes)
        length = int.from_bytes(data[1:5], byteorder="big")

        if length == 0:
            return set(), 6  # Type byte + length (4) + item type (1)

        # Read item type (1 byte)
        item_type = data[5]

        # Start reading from position 6 (after type, length, and item type)
        pos = 6
        result = set()

        if item_type == INTEGER_TYPE:
            for _ in range(length):
                # Read size (4 bytes)
                size = int.from_bytes(data[pos : pos + 4], byteorder="big")
                pos += 4
                # Read value
                value = int.from_bytes(
                    data[pos : pos + size], byteorder="big", signed=True
                )
                pos += size
                result.add(value)

        elif item_type == STRING_TYPE:
            for _ in range(length):
                # Read string length (4 bytes)
                str_length = int.from_bytes(data[pos : pos + 4], byteorder="big")
                pos += 4
                # Read and decode string
                value = data[pos : pos + str_length].decode("utf-8")
                pos += str_length
                result.add(value)

        elif item_type == BOOLEAN_TYPE:
            for _ in range(length):
                # Read boolean value (1 byte) and explicitly create a bool
                result.add(True if data[pos] == 1 else False)
                pos += 1

        elif item_type == COMPRESSED_TYPE:
            # Sets of compressed items are handled differently
            for _ in range(length):
                # Each item has its own compression header
                # Decode it recursively and track consumed bytes
                item_data = data[pos:]
                item, consumed = _decode_with_consumed(item_data)

                # Skip unhashable types
                if isinstance(item, (list, dict)):
                    # Convert to tuple if list, otherwise keep as is (will raise if added to set)
                    if isinstance(item, list):
                        item = tuple(item)

                result.add(item)
                pos += consumed

        elif item_type in (LIST_TYPE, SET_TYPE, DICT_TYPE, SCHEMA_TYPE):
            # Handle nested structures - we need to decode each one completely
            for _ in range(length):
                # Find where this item ends by decoding it
                item_data = data[pos:]
                item, consumed = _decode_with_consumed(item_data)

                # Skip unhashable types
                if isinstance(item, (list, dict)):
                    # Convert to tuple if list, otherwise keep as is (will raise if added to set)
                    if isinstance(item, list):
                        item = tuple(item)

                result.add(item)
                pos += consumed

        else:
            raise ValueError(f"Invalid item type in set: {item_type}")

        return result, pos

    elif type_byte == DICT_TYPE:
        # Read number of key-value pairs (4 bytes)
        count = int.from_bytes(data[1:5], byteorder="big")

        if count == 0:
            return {}, 5  # Type byte + count (4)

        # Start reading from position 5 (after type and count)
        pos = 5
        result = {}

        for _ in range(count):
            # Decode key
            key_data = data[pos:]
            key, key_size = _decode_with_consumed(key_data)
            pos += key_size

            # Decode value
            value_data = data[pos:]
            value, value_size = _decode_with_consumed(value_data)
            pos += value_size

            # Add to result
            result[key] = value

        return result, pos

    elif type_byte == SCHEMA_TYPE:
        # First, decode the schema
        schema_data = data[1:]  # Skip the SCHEMA_TYPE byte
        schema, schema_size = _decode_with_consumed(schema_data)

        # Next, decode the field positions map
        positions_data = data[1 + schema_size :]
        field_positions, positions_size = _decode_with_consumed(positions_data)

        # Decode all fields
        fields_data = data[1 + schema_size + positions_size :]
        pos = 0
        result = {}

        for field_name in schema:
            field_data = fields_data[pos:]
            field_value, consumed = _decode_with_consumed(field_data)
            result[field_name] = field_value
            pos += consumed

        # Total consumed bytes
        total_consumed = 1 + schema_size + positions_size + pos
        return result, total_consumed

    else:
        raise ValueError(f"Invalid type byte: {type_byte}")

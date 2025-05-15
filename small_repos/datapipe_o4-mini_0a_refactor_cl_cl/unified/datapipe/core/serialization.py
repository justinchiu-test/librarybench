"""
Serialization framework for data streams.
"""
import json

# Global registry of serializers
serializers = {}

class SerializerRegistry:
    """
    Object to hold record data and provide serialization methods.
    Used by Social Media Analyst implementation.
    """
    def __init__(self, data):
        self.data = data
    
    def serialize(self, format_name):
        """Serialize data in the specified format"""
        if format_name == 'json':
            return b'JSON:' + json.dumps(self.data).encode('utf-8')
        elif format_name == 'avro':
            # Placeholder for real Avro serialization
            return b'AVRO:' + json.dumps(self.data).encode('utf-8')
        elif format_name == 'parquet':
            # Placeholder for real Parquet serialization
            return b'PARQUET:' + json.dumps(self.data).encode('utf-8')
        else:
            raise ValueError(f"Unsupported format: {format_name}")


def add_serializer(name_or_data, serializer_func=None):
    """
    Register a serializer function or create a SerializerRegistry.
    
    This has two modes:
    1. If called with (name, function) - register the function under that name
    2. If called with (data) - return a SerializerRegistry object for that data
    
    Args:
        name_or_data: Either the name to register or the data to serialize
        serializer_func: The serialization function (None if name_or_data is data)
        
    Returns:
        dict of serializers or SerializerRegistry depending on the mode
    """
    # Mode detection
    if serializer_func is None:
        # This is Social Media Analyst mode - return a SerializerRegistry
        return SerializerRegistry(name_or_data)
    else:
        # This is standard mode - register a serializer
        serializers[name_or_data] = serializer_func
        return serializers


def get_serializer(name):
    """
    Get a serializer by name.
    
    Args:
        name: The name of the serializer to retrieve
        
    Returns:
        The serializer function
    """
    return serializers.get(name)
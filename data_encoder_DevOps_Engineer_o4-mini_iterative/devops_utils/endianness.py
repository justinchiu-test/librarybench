"""
Module for endianness handling.
"""

def endianness_handling(data, endianness='big'):
    """
    Convert between int and bytes considering endianness.

    Args:
        data (int or bytes or bytearray): Data to convert.
        endianness (str): 'big' or 'little'

    Returns:
        bytes or int: Converted value.
    """
    if endianness not in ('big', 'little'):
        raise ValueError("Endianness must be 'big' or 'little'")

    if isinstance(data, int):
        # Determine minimum number of bytes
        length = (data.bit_length() + 7) // 8 or 1
        return data.to_bytes(length, byteorder=endianness, signed=False)
    elif isinstance(data, (bytes, bytearray)):
        return int.from_bytes(bytes(data), byteorder=endianness, signed=False)
    else:
        raise ValueError('Data must be int, bytes, or bytearray')

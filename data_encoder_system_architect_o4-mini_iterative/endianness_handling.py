def endianness_handling(data, byte_order: str):
    """
    If data is int, pack to bytes using byte_order ('big' or 'little').
    If data is bytes or bytearray, unpack to int.
    """
    if byte_order not in ('big', 'little'):
        raise ValueError("byte_order must be 'big' or 'little'")
    if isinstance(data, int):
        if data < 0:
            raise ValueError("Cannot pack negative numbers")
        # Determine minimal length in bytes
        length = (data.bit_length() + 7) // 8 or 1
        return data.to_bytes(length, byteorder=byte_order)
    elif isinstance(data, (bytes, bytearray)):
        return int.from_bytes(data, byteorder=byte_order)
    else:
        raise TypeError("Data must be int, bytes, or bytearray")

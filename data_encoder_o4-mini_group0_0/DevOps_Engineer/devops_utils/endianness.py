from utils import validate_type

def endianness_handling(data, endianness='big'):
    if endianness not in ('big', 'little'):
        raise ValueError("Endianness must be 'big' or 'little'")
    if isinstance(data, int):
        length = (data.bit_length() + 7) // 8 or 1
        return data.to_bytes(length, byteorder=endianness, signed=False)
    elif isinstance(data, (bytes, bytearray)):
        return int.from_bytes(bytes(data), byteorder=endianness, signed=False)
    else:
        raise ValueError('Data must be int, bytes, or bytearray')

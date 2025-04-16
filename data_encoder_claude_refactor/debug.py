from data_encoder import encode, decode
import sys

# Test boolean encoding and decoding
encoded = encode(True)
decoded = decode(encoded)

print(f"Original: {True}, type: {type(True)}")
print(f"Encoded: {encoded}")
print(f"Decoded: {decoded}, type: {type(decoded)}")
print(f"Is instance of bool? {isinstance(decoded, bool)}")
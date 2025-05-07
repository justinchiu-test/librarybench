import json
from typing import Iterable, Union, Generator

def streaming_support(data_stream: Iterable[Union[bytes, bytearray, str, object]]) -> Generator:
    """
    Encode or decode data streams.
    If there is any bytes/bytearray/str in the stream, we treat the stream as 'decode' mode:
      - bytes/bytearray: decode utf-8, skip empty, json.loads
      - str: skip empty, json.loads
      - other objects: pass through unchanged

    If there are no bytes/bytearray/str items at all, we treat the stream as 'encode' mode:
      - all items are JSON-serializable objects: json.dumps with compact separators + newline, then utf-8 bytes
    """
    # Materialize the stream so we can inspect it
    items = list(data_stream)
    # Determine mode: if any item is bytes/bytearray/str, go decode; else encode
    has_textual = any(isinstance(i, (bytes, bytearray, str)) for i in items)
    if has_textual:
        # Decode mode
        for item in items:
            if isinstance(item, (bytes, bytearray)):
                text = item.decode('utf-8')
                if not text:
                    continue
                yield json.loads(text)
            elif isinstance(item, str):
                if not item:
                    continue
                yield json.loads(item)
            else:
                # Pass through any non-bytes/str objects
                yield item
    else:
        # Encode mode
        for item in items:
            # JSON lines: compact separators, newline, then utf-8 bytes
            line = json.dumps(item, separators=(',', ':')) + '\n'
            yield line.encode('utf-8')

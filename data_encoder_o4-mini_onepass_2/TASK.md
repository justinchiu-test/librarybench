# The Task

I need a tool that can take structured data—like strings, numbers, lists—and encode it into a compact binary format for storage or transmission. And of course, it should decode it too. Think of it like a super simplified version of how Protocol Buffers or MessagePack works.

# Requirements

Design a simple binary format that can encode integers, strings, booleans, and homogeneous lists. Implement the encoding from the object into bytes and the decoder from bytes back into the original type. Don't use any existing data library such as pickle, json, etc. 
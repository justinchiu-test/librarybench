# The Task Updated

We want some updated functionality. Version 2 includes support for user-defined schemas, more types, compression support, and field-level access.

# New features to add:

User-Defined Schema

* Add support for user-defined schema, like follows:
```
schema = {
    "name": "str",
    "age": "int",
    "scores": ["int"]
}
encode(obj, schema=schema)
```

More Types

* Can you also support homogeneous sets and non-homogeneous dictionaries?

Compression Option

* Make it an option to compress strings or long sections during encoding. Implement a simple algorithm for now.

Field-level Access

* Add support to extract just one field of the data without decoding everything. 

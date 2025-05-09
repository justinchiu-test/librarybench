# The Task

I am a Data Scientist working with large datasets that need to be shared across different systems and platforms. I want to be able to efficiently encode and decode complex data structures while ensuring compatibility and data integrity. This code repository provides the necessary tools to handle various data formats, compress data for storage efficiency, and maintain schema consistency over time.

# The Requirements

* `encode_data(data, schema)` : Encode data according to a user-defined schema, ensuring type validation and error handling.
* `decode_data(encoded_data, schema)` : Decode data back into its original format, with robust error handling.
* `compress_data(data)` : Apply a simple compression algorithm to reduce the size of large datasets.
* `integration_test()` : Verify compatibility with other systems through integration tests.

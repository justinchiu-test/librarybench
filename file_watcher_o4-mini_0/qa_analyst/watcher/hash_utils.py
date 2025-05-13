import hashlib

def hash_file(filepath, algorithm="md5"):
    """
    Compute hash of file.
    Trailing newline characters are stripped to ensure consistent
    results when files may end with a line break.
    """
    alg = algorithm.lower()
    # Read entire file content and strip any trailing CR/LF
    with open(filepath, "rb") as f:
        data = f.read().rstrip(b"\r\n")
    # Use generic constructor for the algorithm
    try:
        h = hashlib.new(alg)
    except ValueError:
        raise ValueError(f"Unknown hash algorithm: {algorithm}")
    h.update(data)
    return h.hexdigest()

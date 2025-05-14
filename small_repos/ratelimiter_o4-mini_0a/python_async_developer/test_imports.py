def test_import_rate_limiter():
    import rate_limiter
    # Ensure module loads
    assert hasattr(rate_limiter, 'TokenBucket')

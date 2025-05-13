# Expose the MockServer, HttpClient, and Response at the package level
from .mockserver import MockServer, HttpClient, Response

# Also make this package available under the bare name "mockserver"
import sys
# Map the fully‐qualified package module to the name "mockserver"
sys.modules['mockserver'] = sys.modules[__name__]

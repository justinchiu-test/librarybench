# FeatureStore

A specialized in-memory database optimized for machine learning workflows that provides efficient storage and retrieval of feature vectors, with built-in support for similarity searches, versioning, batch operations, and A/B testing.

## Key Features

- **Optimized Vector Storage**: Specialized storage for dense and sparse high-dimensional vectors with efficient indexing
- **Multiple Distance Metrics**: Native support for Euclidean, cosine, Manhattan, and Mahalanobis distance calculations
- **Feature Versioning**: Maintains historical versions of features with point-in-time retrieval capabilities
- **Efficient Batch Operations**: Vectorized data retrieval optimized for batch inference scenarios
- **Automatic Feature Transformations**: In-database preprocessing and transformation with consistency guarantees
- **A/B Testing Support**: Deterministic entity assignment to experimental groups with configurable traffic splitting

## Installation

```bash
uv sync
```

## Usage

```python
from feature_store import FeatureStore
from feature_store.vectors import DenseVector
from feature_store.transformations import StandardScaler

# Create a feature store instance
store = FeatureStore()

# Store feature vectors
store.add("user:123", DenseVector([1.2, 3.4, 5.6]), feature_group="user_embeddings")

# Retrieve vectors with similarity search
similar_users = store.query_similar("user:123", k=10, distance="cosine")

# Apply transformations during retrieval
scaler = StandardScaler()
store.register_transformation("user_embeddings", scaler)
normalized_vector = store.get("user:123", apply_transformations=True)

# Batch operations
user_ids = ["user:123", "user:456", "user:789"]
feature_batch = store.batch_get(user_ids, feature_group="user_embeddings")

# Feature versioning
store.add_version("user:123", DenseVector([1.3, 3.5, 5.7]), version="v2")
historical_vector = store.get("user:123", version="v1")

# A/B testing
store.create_experiment("embedding_model_comparison", groups=["control", "treatment"], weights=[0.5, 0.5])
group = store.get_experiment_group("user:123", experiment="embedding_model_comparison")
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

## Requirements

- Python 3.10+
- NumPy, SciPy, scikit-learn
- Pandas
- Pydantic
- FAISS (for vector indexing)
"""
Encoding transformations for categorical features.
"""

from typing import Dict, List, Optional, Tuple, Union, cast, Any, Set

import numpy as np
from pydantic import Field

from feature_store.transformations.base import Transformation
from feature_store.vectors.base import VectorBase
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.sparse import SparseVector


class OneHotEncoder(Transformation):
    """
    Encode categorical integer features as a one-hot numeric array.
    
    This transformer will encode categorical features with an integer value
    between 0 and n_categories-1 into a one-hot vector of size n_categories.
    """

    name: str = Field("onehot_encoder", const=True)
    sparse: bool = Field(True, description="Whether to use sparse representation for transformed vectors")
    categories_: Optional[List[List[int]]] = Field(None, description="Categories for each feature")
    n_features_: Optional[int] = Field(None, description="Number of features")
    feature_indices_: Optional[np.ndarray] = Field(None, description="Indices for each feature")
    
    def fit(self, vectors: List[VectorBase]) -> "OneHotEncoder":
        """Fit the transformer to the data.
        
        Determines the set of categories for each feature.
        
        Args:
            vectors: List of vectors to fit the transformation to
            
        Returns:
            Self, for method chaining
        """
        if not vectors:
            raise ValueError("Cannot fit OneHotEncoder on empty list")
        
        # Ensure all vectors are the same dimensionality
        dims = [len(v) for v in vectors]
        if len(set(dims)) != 1:
            raise ValueError(f"All vectors must have the same dimensionality, got {set(dims)}")
        
        self.n_features_ = dims[0]
        
        # Convert all vectors to arrays
        arrays = [v.to_array() for v in vectors]
        data = np.vstack(arrays).astype(int)
        
        # Determine categories for each feature
        self.categories_ = []
        for i in range(self.n_features_):
            feature_data = data[:, i]
            # Extract unique values and sort them (excluding negative values)
            categories = sorted(set(int(x) for x in feature_data if x >= 0))
            self.categories_.append(categories)
        
        # Calculate feature indices for transforming data
        self.feature_indices_ = np.zeros(self.n_features_ + 1, dtype=np.int32)
        for i in range(self.n_features_):
            self.feature_indices_[i + 1] = self.feature_indices_[i] + len(self.categories_[i])
        
        self.is_fitted = True
        return self
    
    def transform(self, vector: VectorBase) -> VectorBase:
        """Apply the transformation to a vector.
        
        Args:
            vector: Vector to transform
            
        Returns:
            Transformed vector
        """
        self._check_is_fitted()
        
        # Get data as array
        data = vector.to_array().astype(int)
        
        if len(data) != self.n_features_:
            raise ValueError(f"Vector has wrong dimensionality: {len(data)} != {self.n_features_}")
        
        # Calculate output dimensionality
        n_dims = self.feature_indices_[-1]
        
        if self.sparse:
            # Build sparse vector
            indices = []
            values = []
            
            for feature_idx in range(self.n_features_):
                category = data[feature_idx]
                # Check if category is valid (non-negative and in categories)
                if category >= 0 and category in self.categories_[feature_idx]:
                    # Find position of category in the list
                    category_idx = self.categories_[feature_idx].index(category)
                    # Calculate position in output vector
                    output_idx = self.feature_indices_[feature_idx] + category_idx
                    indices.append(output_idx)
                    values.append(1.0)
            
            # Create sparse vector
            return SparseVector(
                indices=np.array(indices, dtype=np.int32),
                values=np.array(values, dtype=np.float32),
                dimensionality=n_dims
            )
        else:
            # Build dense vector
            transformed = np.zeros(n_dims, dtype=np.float32)
            
            for feature_idx in range(self.n_features_):
                category = data[feature_idx]
                # Check if category is valid (non-negative and in categories)
                if category >= 0 and category in self.categories_[feature_idx]:
                    # Find position of category in the list
                    category_idx = self.categories_[feature_idx].index(category)
                    # Calculate position in output vector
                    output_idx = self.feature_indices_[feature_idx] + category_idx
                    transformed[output_idx] = 1.0
            
            # Create dense vector
            return DenseVector(transformed)
    
    def inverse_transform(self, vector: VectorBase) -> VectorBase:
        """Apply the inverse transformation to a vector.
        
        Args:
            vector: Vector to inverse transform
            
        Returns:
            Inverse transformed vector
        """
        self._check_is_fitted()
        
        # Get data as array
        data = vector.to_array()
        
        if len(data) != self.feature_indices_[-1]:
            raise ValueError(f"Vector has wrong dimensionality: {len(data)} != {self.feature_indices_[-1]}")
        
        # Initialize output
        inverse_transformed = np.zeros(self.n_features_, dtype=np.float32)
        
        for feature_idx in range(self.n_features_):
            start = self.feature_indices_[feature_idx]
            end = self.feature_indices_[feature_idx + 1]
            # Extract the one-hot encoded part for this feature
            feature_data = data[start:end]
            
            # Find the position of the maximum value (the one-hot encoded position)
            if np.any(feature_data):
                max_idx = np.argmax(feature_data)
                # Convert back to original category
                inverse_transformed[feature_idx] = self.categories_[feature_idx][max_idx]
        
        # Return as dense vector
        return DenseVector(inverse_transformed)
    
    def transform_many(self, vectors: List[VectorBase]) -> List[VectorBase]:
        """Apply the transformation to multiple vectors.
        
        Args:
            vectors: List of vectors to transform
            
        Returns:
            List of transformed vectors
        """
        return [self.transform(v) for v in vectors]
    
    def _get_additional_state(self) -> Dict[str, Any]:
        """Get additional state specific to the transformation.
        
        Returns:
            Dictionary of additional state
        """
        return {
            "sparse": self.sparse,
            "n_features_": self.n_features_,
            "categories_": self.categories_,
            "feature_indices_": self.feature_indices_.tolist() if self.feature_indices_ is not None else None
        }
    
    def _set_additional_state(self, state: Dict[str, Any]) -> None:
        """Set additional state specific to the transformation.
        
        Args:
            state: Dictionary of state
        """
        self.sparse = state["sparse"]
        self.n_features_ = state["n_features_"]
        self.categories_ = state["categories_"]
        if state["feature_indices_"] is not None:
            self.feature_indices_ = np.array(state["feature_indices_"], dtype=np.int32)


class LabelEncoder(Transformation):
    """
    Encode categorical string labels as integers.
    
    This transformer encodes string labels into integers between 0 and n_classes-1.
    """

    name: str = Field("label_encoder", const=True)
    classes_: Optional[List[str]] = Field(None, description="Classes seen during fit")
    
    def fit(self, vectors: List[VectorBase]) -> "LabelEncoder":
        """Fit the transformer to the data.
        
        Args:
            vectors: List of vectors to fit the transformation to. Each vector
                    should be a one-dimensional vector (scalar) containing the
                    string label as bytes.
            
        Returns:
            Self, for method chaining
        """
        if not vectors:
            raise ValueError("Cannot fit LabelEncoder on empty list")
        
        # For label encoder, we expect each vector to be a one-dimensional
        # vector (scalar) containing the string label as bytes
        labels = []
        for v in vectors:
            data = v.to_array()
            if len(data) != 1:
                raise ValueError(f"Each vector must be one-dimensional, got {len(data)}")
            # Decode bytes to string
            label = str(data[0])
            labels.append(label)
        
        # Get unique classes and sort
        self.classes_ = sorted(set(labels))
        
        self.is_fitted = True
        return self
    
    def transform(self, vector: VectorBase) -> VectorBase:
        """Apply the transformation to a vector.
        
        Args:
            vector: Vector to transform
            
        Returns:
            Transformed vector
        """
        self._check_is_fitted()
        
        # Get data as array
        data = vector.to_array()
        
        if len(data) != 1:
            raise ValueError(f"Vector must be one-dimensional, got {len(data)}")
        
        # Decode bytes to string
        label = str(data[0])
        
        # Convert to integer
        try:
            idx = self.classes_.index(label)
        except ValueError:
            raise ValueError(f"Unknown label: {label}")
        
        # Return as dense vector
        return DenseVector([float(idx)])
    
    def inverse_transform(self, vector: VectorBase) -> VectorBase:
        """Apply the inverse transformation to a vector.
        
        Args:
            vector: Vector to inverse transform
            
        Returns:
            Inverse transformed vector
        """
        self._check_is_fitted()
        
        # Get data as array
        data = vector.to_array()
        
        if len(data) != 1:
            raise ValueError(f"Vector must be one-dimensional, got {len(data)}")
        
        # Convert to integer
        idx = int(data[0])
        
        if idx < 0 or idx >= len(self.classes_):
            raise ValueError(f"Index {idx} out of range")
        
        # Convert to string
        label = self.classes_[idx]
        
        # Convert to bytes and return as dense vector
        return DenseVector([float(ord(label[0]))])
    
    def transform_many(self, vectors: List[VectorBase]) -> List[VectorBase]:
        """Apply the transformation to multiple vectors.
        
        Args:
            vectors: List of vectors to transform
            
        Returns:
            List of transformed vectors
        """
        return [self.transform(v) for v in vectors]
    
    def _get_additional_state(self) -> Dict[str, Any]:
        """Get additional state specific to the transformation.
        
        Returns:
            Dictionary of additional state
        """
        return {
            "classes_": self.classes_
        }
    
    def _set_additional_state(self, state: Dict[str, Any]) -> None:
        """Set additional state specific to the transformation.
        
        Args:
            state: Dictionary of state
        """
        self.classes_ = state["classes_"]
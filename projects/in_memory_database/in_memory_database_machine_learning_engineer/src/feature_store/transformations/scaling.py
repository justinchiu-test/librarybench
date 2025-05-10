"""
Scaling transformations for normalizing feature vectors.
"""

from typing import Dict, List, Optional, Tuple, Union, cast, Any

import numpy as np
from pydantic import Field

from feature_store.transformations.base import Transformation
from feature_store.vectors.base import VectorBase
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.sparse import SparseVector


class StandardScaler(Transformation):
    """
    Standardize features by removing the mean and scaling to unit variance.
    
    The transformation is given by:
        X_scaled = (X - mean) / std
    
    Where mean and std are estimated from the training data.
    """

    name: str = Field("standard_scaler", const=True)
    with_mean: bool = Field(True, description="Center the data before scaling")
    with_std: bool = Field(True, description="Scale the data to unit variance")
    mean_: Optional[np.ndarray] = Field(None, description="Mean of the training data")
    scale_: Optional[np.ndarray] = Field(None, description="Standard deviation of the training data")
    
    def fit(self, vectors: List[VectorBase]) -> "StandardScaler":
        """Fit the transformer to the data.
        
        Computes the mean and standard deviation of the training data
        to be used for later scaling.
        
        Args:
            vectors: List of vectors to fit the transformation to
            
        Returns:
            Self, for method chaining
        """
        if not vectors:
            raise ValueError("Cannot fit StandardScaler on empty list")
        
        # Convert all vectors to arrays
        arrays = [v.to_array() for v in vectors]
        data = np.vstack(arrays)
        
        # Calculate mean if requested
        if self.with_mean:
            self.mean_ = np.mean(data, axis=0)
        else:
            self.mean_ = np.zeros(data.shape[1], dtype=np.float32)
        
        # Calculate standard deviation if requested
        if self.with_std:
            self.scale_ = np.std(data, axis=0, ddof=1)
            # Handle zeros in scale (avoid division by zero)
            self.scale_ = np.where(self.scale_ == 0, 1.0, self.scale_)
        else:
            self.scale_ = np.ones(data.shape[1], dtype=np.float32)
        
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
        
        # Apply transformation
        transformed = (data - self.mean_) / self.scale_
        
        # Return as same type as input
        if isinstance(vector, DenseVector):
            return DenseVector(transformed)
        elif isinstance(vector, SparseVector):
            # For sparse vectors, we need to recreate the sparse representation
            # Note: standardization may make the vector dense
            indices = np.nonzero(transformed)[0]
            values = transformed[indices]
            return SparseVector(indices=indices, values=values, dimensionality=len(transformed))
        else:
            raise TypeError(f"Unsupported vector type: {type(vector)}")
    
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
        
        # Apply inverse transformation
        inverse_transformed = data * self.scale_ + self.mean_
        
        # Return as same type as input
        if isinstance(vector, DenseVector):
            return DenseVector(inverse_transformed)
        elif isinstance(vector, SparseVector):
            # For sparse vectors, we need to recreate the sparse representation
            indices = np.nonzero(inverse_transformed)[0]
            values = inverse_transformed[indices]
            return SparseVector(indices=indices, values=values, dimensionality=len(inverse_transformed))
        else:
            raise TypeError(f"Unsupported vector type: {type(vector)}")
    
    def transform_many(self, vectors: List[VectorBase]) -> List[VectorBase]:
        """Apply the transformation to multiple vectors.
        
        Args:
            vectors: List of vectors to transform
            
        Returns:
            List of transformed vectors
        """
        self._check_is_fitted()
        
        # Convert all vectors to arrays
        arrays = [v.to_array() for v in vectors]
        data = np.vstack(arrays)
        
        # Apply transformation
        transformed = (data - self.mean_) / self.scale_
        
        # Return as same type as input
        result = []
        for i, v in enumerate(vectors):
            if isinstance(v, DenseVector):
                result.append(DenseVector(transformed[i]))
            elif isinstance(v, SparseVector):
                indices = np.nonzero(transformed[i])[0]
                values = transformed[i][indices]
                result.append(SparseVector(indices=indices, values=values, dimensionality=len(transformed[i])))
            else:
                raise TypeError(f"Unsupported vector type: {type(v)}")
        
        return result
    
    def _get_additional_state(self) -> Dict[str, Any]:
        """Get additional state specific to the transformation.
        
        Returns:
            Dictionary of additional state
        """
        return {
            "with_mean": self.with_mean,
            "with_std": self.with_std,
            "mean_": self.mean_.tolist() if self.mean_ is not None else None,
            "scale_": self.scale_.tolist() if self.scale_ is not None else None
        }
    
    def _set_additional_state(self, state: Dict[str, Any]) -> None:
        """Set additional state specific to the transformation.
        
        Args:
            state: Dictionary of state
        """
        self.with_mean = state["with_mean"]
        self.with_std = state["with_std"]
        if state["mean_"] is not None:
            self.mean_ = np.array(state["mean_"], dtype=np.float32)
        if state["scale_"] is not None:
            self.scale_ = np.array(state["scale_"], dtype=np.float32)


class MinMaxScaler(Transformation):
    """
    Scale features to a given range.
    
    The transformation is given by:
        X_scaled = (X - min) / (max - min) * (feature_range[1] - feature_range[0]) + feature_range[0]
    
    Where min and max are estimated from the training data.
    """

    name: str = Field("minmax_scaler", const=True)
    feature_range: Tuple[float, float] = Field((0, 1), description="Desired range of transformed data")
    min_: Optional[np.ndarray] = Field(None, description="Minimum of the training data")
    max_: Optional[np.ndarray] = Field(None, description="Maximum of the training data")
    scale_: Optional[np.ndarray] = Field(None, description="Scaling factor")
    
    def fit(self, vectors: List[VectorBase]) -> "MinMaxScaler":
        """Fit the transformer to the data.
        
        Computes the min and max of the training data to be used for later scaling.
        
        Args:
            vectors: List of vectors to fit the transformation to
            
        Returns:
            Self, for method chaining
        """
        if not vectors:
            raise ValueError("Cannot fit MinMaxScaler on empty list")
        
        # Convert all vectors to arrays
        arrays = [v.to_array() for v in vectors]
        data = np.vstack(arrays)
        
        # Calculate min and max
        self.min_ = np.min(data, axis=0)
        self.max_ = np.max(data, axis=0)
        
        # Calculate scaling factor
        data_range = self.max_ - self.min_
        # Handle zeros in range (avoid division by zero)
        data_range = np.where(data_range == 0, 1.0, data_range)
        
        self.scale_ = (self.feature_range[1] - self.feature_range[0]) / data_range
        
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
        
        # Apply transformation
        transformed = self.scale_ * (data - self.min_) + self.feature_range[0]
        
        # Return as same type as input
        if isinstance(vector, DenseVector):
            return DenseVector(transformed)
        elif isinstance(vector, SparseVector):
            # For sparse vectors, we need to recreate the sparse representation
            indices = np.nonzero(transformed)[0]
            values = transformed[indices]
            return SparseVector(indices=indices, values=values, dimensionality=len(transformed))
        else:
            raise TypeError(f"Unsupported vector type: {type(vector)}")
    
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
        
        # Apply inverse transformation
        inverse_transformed = (data - self.feature_range[0]) / self.scale_ + self.min_
        
        # Return as same type as input
        if isinstance(vector, DenseVector):
            return DenseVector(inverse_transformed)
        elif isinstance(vector, SparseVector):
            # For sparse vectors, we need to recreate the sparse representation
            indices = np.nonzero(inverse_transformed)[0]
            values = inverse_transformed[indices]
            return SparseVector(indices=indices, values=values, dimensionality=len(inverse_transformed))
        else:
            raise TypeError(f"Unsupported vector type: {type(vector)}")
    
    def transform_many(self, vectors: List[VectorBase]) -> List[VectorBase]:
        """Apply the transformation to multiple vectors.
        
        Args:
            vectors: List of vectors to transform
            
        Returns:
            List of transformed vectors
        """
        self._check_is_fitted()
        
        # Convert all vectors to arrays
        arrays = [v.to_array() for v in vectors]
        data = np.vstack(arrays)
        
        # Apply transformation
        transformed = self.scale_ * (data - self.min_) + self.feature_range[0]
        
        # Return as same type as input
        result = []
        for i, v in enumerate(vectors):
            if isinstance(v, DenseVector):
                result.append(DenseVector(transformed[i]))
            elif isinstance(v, SparseVector):
                indices = np.nonzero(transformed[i])[0]
                values = transformed[i][indices]
                result.append(SparseVector(indices=indices, values=values, dimensionality=len(transformed[i])))
            else:
                raise TypeError(f"Unsupported vector type: {type(v)}")
        
        return result
    
    def _get_additional_state(self) -> Dict[str, Any]:
        """Get additional state specific to the transformation.
        
        Returns:
            Dictionary of additional state
        """
        return {
            "feature_range": self.feature_range,
            "min_": self.min_.tolist() if self.min_ is not None else None,
            "max_": self.max_.tolist() if self.max_ is not None else None,
            "scale_": self.scale_.tolist() if self.scale_ is not None else None
        }
    
    def _set_additional_state(self, state: Dict[str, Any]) -> None:
        """Set additional state specific to the transformation.
        
        Args:
            state: Dictionary of state
        """
        self.feature_range = state["feature_range"]
        if state["min_"] is not None:
            self.min_ = np.array(state["min_"], dtype=np.float32)
        if state["max_"] is not None:
            self.max_ = np.array(state["max_"], dtype=np.float32)
        if state["scale_"] is not None:
            self.scale_ = np.array(state["scale_"], dtype=np.float32)
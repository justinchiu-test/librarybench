from datetime import datetime
from typing import Dict, List, Optional, Set, Union, Any
from uuid import UUID, uuid4

from .models import (
    Dataset, 
    DatasetVersion, 
    DataTransformation, 
    TaskDatasetLink, 
    DatasetFormat,
    DatasetStorageType,
    DataTransformationType
)
from .storage import DatasetStorageInterface


class DatasetService:
    """Service for managing datasets and their versions."""
    
    def __init__(self, storage: DatasetStorageInterface):
        """
        Initialize the dataset service.
        
        Args:
            storage: The storage implementation to use
        """
        self._storage = storage
    
    # Dataset operations
    
    def create_dataset(
        self,
        name: str,
        description: Optional[str] = None,
        format: Union[DatasetFormat, str] = DatasetFormat.CSV,
        storage_type: Union[DatasetStorageType, str] = DatasetStorageType.LOCAL,
        location: str = "",
        size_bytes: Optional[int] = None,
        row_count: Optional[int] = None,
        column_count: Optional[int] = None,
        schema: Optional[Dict[str, str]] = None,
        tags: Optional[Set[str]] = None,
        hash: Optional[str] = None,
        version: Optional[str] = None,
    ) -> Dataset:
        """
        Create a new dataset.
        
        Args:
            name: Dataset name
            description: Dataset description
            format: Dataset format
            storage_type: Type of storage
            location: Path or URL to the dataset
            size_bytes: Size of the dataset in bytes
            row_count: Number of rows
            column_count: Number of columns
            schema: Data schema (column name -> data type)
            tags: Tags for categorization
            hash: Content hash for verification
            version: Version identifier
            
        Returns:
            Dataset: The created dataset
        """
        # Convert string enums to enum values if needed
        if isinstance(format, str):
            format = DatasetFormat(format)
        
        if isinstance(storage_type, str):
            storage_type = DatasetStorageType(storage_type)
        
        # Create the dataset
        dataset = Dataset(
            name=name,
            description=description,
            format=format,
            storage_type=storage_type,
            location=location,
            size_bytes=size_bytes,
            row_count=row_count,
            column_count=column_count,
            schema=schema or {},
            tags=tags or set(),
            hash=hash,
            version=version,
        )
        
        # Save the dataset
        self._storage.create_dataset(dataset)
        
        return dataset
    
    def get_dataset(self, dataset_id: UUID) -> Optional[Dataset]:
        """
        Retrieve a dataset by ID.
        
        Args:
            dataset_id: The ID of the dataset to retrieve
            
        Returns:
            Optional[Dataset]: The dataset if found, None otherwise
        """
        return self._storage.get_dataset(dataset_id)
    
    def update_dataset(
        self,
        dataset_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        size_bytes: Optional[int] = None,
        row_count: Optional[int] = None,
        column_count: Optional[int] = None,
        schema: Optional[Dict[str, str]] = None,
        hash: Optional[str] = None,
        version: Optional[str] = None,
    ) -> bool:
        """
        Update an existing dataset.
        
        Args:
            dataset_id: The ID of the dataset to update
            name: New dataset name
            description: New dataset description
            location: New path or URL
            size_bytes: New size in bytes
            row_count: New row count
            column_count: New column count
            schema: New schema
            hash: New content hash
            version: New version identifier
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            ValueError: If dataset doesn't exist
        """
        dataset = self._storage.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} does not exist")
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if location is not None:
            update_data["location"] = location
        if size_bytes is not None:
            update_data["size_bytes"] = size_bytes
        if row_count is not None:
            update_data["row_count"] = row_count
        if column_count is not None:
            update_data["column_count"] = column_count
        if schema is not None:
            update_data["schema"] = schema
        if hash is not None:
            update_data["hash"] = hash
        if version is not None:
            update_data["version"] = version
        
        dataset.update(**update_data)
        return self._storage.update_dataset(dataset)
    
    def delete_dataset(self, dataset_id: UUID) -> bool:
        """
        Delete a dataset and all its versions.
        
        Args:
            dataset_id: The ID of the dataset to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete_dataset(dataset_id)
    
    def list_datasets(
        self, format: Optional[Union[DatasetFormat, str]] = None, tags: Optional[Set[str]] = None
    ) -> List[Dataset]:
        """
        List datasets with optional filtering.
        
        Args:
            format: Filter by dataset format
            tags: Filter by tags (datasets must have all specified tags)
            
        Returns:
            List[Dataset]: List of datasets matching the criteria
        """
        if isinstance(format, DatasetFormat):
            format = format.value
            
        return self._storage.list_datasets(format, tags)
    
    def add_tag_to_dataset(self, dataset_id: UUID, tag: str) -> bool:
        """
        Add a tag to a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            tag: The tag to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If dataset doesn't exist
        """
        dataset = self._storage.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} does not exist")
        
        dataset.add_tag(tag)
        return self._storage.update_dataset(dataset)
    
    def remove_tag_from_dataset(self, dataset_id: UUID, tag: str) -> bool:
        """
        Remove a tag from a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            tag: The tag to remove
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If dataset doesn't exist
        """
        dataset = self._storage.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} does not exist")
        
        dataset.remove_tag(tag)
        return self._storage.update_dataset(dataset)
    
    def update_dataset_metadata(
        self, dataset_id: UUID, key: str, value: Union[str, int, float, bool, list, dict]
    ) -> bool:
        """
        Update a custom metadata field for a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            key: The metadata key
            value: The metadata value
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If dataset doesn't exist
        """
        dataset = self._storage.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} does not exist")
        
        dataset.update_custom_metadata(key, value)
        return self._storage.update_dataset(dataset)
    
    # Dataset version operations
    
    def create_version(
        self,
        dataset_id: UUID,
        version_number: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        creator: Optional[str] = None,
        hash: Optional[str] = None,
        size_bytes: Optional[int] = None,
        row_count: Optional[int] = None,
        column_count: Optional[int] = None,
        schema: Optional[Dict[str, str]] = None,
        parent_version_id: Optional[UUID] = None,
    ) -> DatasetVersion:
        """
        Create a new version of a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            version_number: Version number or identifier
            description: Version description
            location: Path or URL to this specific version
            creator: Who created this version
            hash: Content hash for verification
            size_bytes: Size in bytes
            row_count: Number of rows
            column_count: Number of columns
            schema: Data schema (column name -> data type)
            parent_version_id: ID of the parent version
            
        Returns:
            DatasetVersion: The created version
            
        Raises:
            ValueError: If dataset or parent version doesn't exist
        """
        # Check if dataset exists
        dataset = self._storage.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} does not exist")
        
        # Check if parent version exists
        if parent_version_id:
            parent_version = self._storage.get_dataset_version(parent_version_id)
            if not parent_version:
                raise ValueError(f"Parent version with ID {parent_version_id} does not exist")
            
            # Ensure parent version belongs to the same dataset
            if parent_version.dataset_id != dataset_id:
                raise ValueError("Parent version belongs to a different dataset")
        
        # Create version
        version = DatasetVersion(
            dataset_id=dataset_id,
            version_number=version_number,
            description=description,
            location=location or dataset.location,
            creator=creator,
            hash=hash,
            size_bytes=size_bytes,
            row_count=row_count,
            column_count=column_count,
            schema=schema or {},
            parent_version_id=parent_version_id,
        )
        
        # Save version
        self._storage.create_dataset_version(version)
        
        return version
    
    def get_version(self, version_id: UUID) -> Optional[DatasetVersion]:
        """
        Retrieve a dataset version by ID.
        
        Args:
            version_id: The ID of the version to retrieve
            
        Returns:
            Optional[DatasetVersion]: The version if found, None otherwise
        """
        return self._storage.get_dataset_version(version_id)
    
    def update_version(
        self,
        version_id: UUID,
        description: Optional[str] = None,
        location: Optional[str] = None,
        hash: Optional[str] = None,
        size_bytes: Optional[int] = None,
        row_count: Optional[int] = None,
        column_count: Optional[int] = None,
        schema: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Update an existing dataset version.
        
        Args:
            version_id: The ID of the version to update
            description: New description
            location: New path or URL
            hash: New content hash
            size_bytes: New size in bytes
            row_count: New row count
            column_count: New column count
            schema: New schema
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            ValueError: If version doesn't exist
        """
        version = self._storage.get_dataset_version(version_id)
        if not version:
            raise ValueError(f"Dataset version with ID {version_id} does not exist")
        
        update_data = {}
        if description is not None:
            update_data["description"] = description
        if location is not None:
            update_data["location"] = location
        if hash is not None:
            update_data["hash"] = hash
        if size_bytes is not None:
            update_data["size_bytes"] = size_bytes
        if row_count is not None:
            update_data["row_count"] = row_count
        if column_count is not None:
            update_data["column_count"] = column_count
        if schema is not None:
            update_data["schema"] = schema
        
        version.update(**update_data)
        return self._storage.update_dataset_version(version)
    
    def delete_version(self, version_id: UUID) -> bool:
        """
        Delete a dataset version.
        
        Args:
            version_id: The ID of the version to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete_dataset_version(version_id)
    
    def list_versions(
        self, dataset_id: UUID, include_lineage: bool = False
    ) -> List[DatasetVersion]:
        """
        List versions of a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            include_lineage: Whether to include full version lineage
            
        Returns:
            List[DatasetVersion]: List of dataset versions
            
        Raises:
            ValueError: If dataset doesn't exist
        """
        dataset = self._storage.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} does not exist")
        
        return self._storage.list_dataset_versions(dataset_id, include_lineage)
    
    def get_version_lineage(self, version_id: UUID) -> List[DatasetVersion]:
        """
        Get the complete version lineage for a dataset version.
        
        Args:
            version_id: The ID of the dataset version
            
        Returns:
            List[DatasetVersion]: List of versions in lineage order (oldest first)
            
        Raises:
            ValueError: If version doesn't exist
        """
        version = self._storage.get_dataset_version(version_id)
        if not version:
            raise ValueError(f"Dataset version with ID {version_id} does not exist")
        
        lineage = []
        current = version
        
        # First, walk backwards to find the root
        ancestor_chain = []
        while current:
            ancestor_chain.insert(0, current)
            if current.parent_version_id:
                current = self._storage.get_dataset_version(current.parent_version_id)
            else:
                break
        
        return ancestor_chain
    
    def update_version_metadata(
        self, version_id: UUID, key: str, value: Union[str, int, float, bool, list, dict]
    ) -> bool:
        """
        Update a custom metadata field for a dataset version.
        
        Args:
            version_id: The ID of the dataset version
            key: The metadata key
            value: The metadata value
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If version doesn't exist
        """
        version = self._storage.get_dataset_version(version_id)
        if not version:
            raise ValueError(f"Dataset version with ID {version_id} does not exist")
        
        version.update_custom_metadata(key, value)
        return self._storage.update_dataset_version(version)
    
    # Data transformation operations
    
    def create_transformation(
        self,
        input_version_id: UUID,
        output_version_id: UUID,
        type: Union[DataTransformationType, str],
        name: str,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        code_reference: Optional[str] = None,
        execution_time_seconds: Optional[float] = None,
        tags: Optional[Set[str]] = None,
    ) -> DataTransformation:
        """
        Create a new data transformation.
        
        Args:
            input_version_id: ID of the input dataset version
            output_version_id: ID of the output dataset version
            type: Type of transformation
            name: Name of the transformation
            description: Description of the transformation
            parameters: Parameters used in the transformation
            code_reference: Reference to the code that performed the transformation
            execution_time_seconds: How long the transformation took
            tags: Tags for categorization
            
        Returns:
            DataTransformation: The created transformation
            
        Raises:
            ValueError: If versions don't exist
        """
        # Check if versions exist
        input_version = self._storage.get_dataset_version(input_version_id)
        if not input_version:
            raise ValueError(f"Input version with ID {input_version_id} does not exist")
        
        output_version = self._storage.get_dataset_version(output_version_id)
        if not output_version:
            raise ValueError(f"Output version with ID {output_version_id} does not exist")
        
        # Convert string enum to enum value if needed
        if isinstance(type, str):
            type = DataTransformationType(type)
        
        # Create transformation
        transformation = DataTransformation(
            type=type,
            name=name,
            description=description,
            input_dataset_version_id=input_version_id,
            output_dataset_version_id=output_version_id,
            parameters=parameters or {},
            code_reference=code_reference,
            execution_time_seconds=execution_time_seconds,
            tags=tags or set(),
        )
        
        # Save transformation
        self._storage.create_data_transformation(transformation)
        
        return transformation
    
    def get_transformation(self, transformation_id: UUID) -> Optional[DataTransformation]:
        """
        Retrieve a data transformation by ID.
        
        Args:
            transformation_id: The ID of the transformation to retrieve
            
        Returns:
            Optional[DataTransformation]: The transformation if found, None otherwise
        """
        return self._storage.get_data_transformation(transformation_id)
    
    def update_transformation(
        self,
        transformation_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        code_reference: Optional[str] = None,
        execution_time_seconds: Optional[float] = None,
    ) -> bool:
        """
        Update an existing data transformation.
        
        Args:
            transformation_id: The ID of the transformation to update
            name: New name
            description: New description
            code_reference: New code reference
            execution_time_seconds: New execution time
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            ValueError: If transformation doesn't exist
        """
        transformation = self._storage.get_data_transformation(transformation_id)
        if not transformation:
            raise ValueError(f"Transformation with ID {transformation_id} does not exist")
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if code_reference is not None:
            update_data["code_reference"] = code_reference
        if execution_time_seconds is not None:
            update_data["execution_time_seconds"] = execution_time_seconds
        
        transformation.update(**update_data)
        return self._storage.update_data_transformation(transformation)
    
    def delete_transformation(self, transformation_id: UUID) -> bool:
        """
        Delete a data transformation.
        
        Args:
            transformation_id: The ID of the transformation to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete_data_transformation(transformation_id)
    
    def list_transformations(self, dataset_id: UUID) -> List[DataTransformation]:
        """
        List all transformations related to a dataset.
        
        Args:
            dataset_id: The ID of the dataset
            
        Returns:
            List[DataTransformation]: List of data transformations
            
        Raises:
            ValueError: If dataset doesn't exist
        """
        dataset = self._storage.get_dataset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} does not exist")
        
        return self._storage.list_transformations_for_dataset(dataset_id)
    
    def get_transformation_lineage(self, version_id: UUID) -> List[DataTransformation]:
        """
        Get the complete transformation lineage for a dataset version.
        
        Args:
            version_id: The ID of the dataset version
            
        Returns:
            List[DataTransformation]: List of transformations in lineage order
            
        Raises:
            ValueError: If version doesn't exist
        """
        version = self._storage.get_dataset_version(version_id)
        if not version:
            raise ValueError(f"Dataset version with ID {version_id} does not exist")
        
        return self._storage.get_transformation_lineage(version_id)
    
    def add_tag_to_transformation(self, transformation_id: UUID, tag: str) -> bool:
        """
        Add a tag to a transformation.
        
        Args:
            transformation_id: The ID of the transformation
            tag: The tag to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If transformation doesn't exist
        """
        transformation = self._storage.get_data_transformation(transformation_id)
        if not transformation:
            raise ValueError(f"Transformation with ID {transformation_id} does not exist")
        
        transformation.add_tag(tag)
        return self._storage.update_data_transformation(transformation)
    
    def remove_tag_from_transformation(self, transformation_id: UUID, tag: str) -> bool:
        """
        Remove a tag from a transformation.
        
        Args:
            transformation_id: The ID of the transformation
            tag: The tag to remove
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If transformation doesn't exist
        """
        transformation = self._storage.get_data_transformation(transformation_id)
        if not transformation:
            raise ValueError(f"Transformation with ID {transformation_id} does not exist")
        
        transformation.remove_tag(tag)
        return self._storage.update_data_transformation(transformation)
    
    def add_note_to_transformation(self, transformation_id: UUID, note: str) -> bool:
        """
        Add a note to a transformation.
        
        Args:
            transformation_id: The ID of the transformation
            note: The note to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If transformation doesn't exist
        """
        transformation = self._storage.get_data_transformation(transformation_id)
        if not transformation:
            raise ValueError(f"Transformation with ID {transformation_id} does not exist")
        
        transformation.add_note(note)
        return self._storage.update_data_transformation(transformation)
    
    def update_transformation_parameter(
        self, transformation_id: UUID, key: str, value: Union[str, int, float, bool, list, dict]
    ) -> bool:
        """
        Update a transformation parameter.
        
        Args:
            transformation_id: The ID of the transformation
            key: The parameter key
            value: The parameter value
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If transformation doesn't exist
        """
        transformation = self._storage.get_data_transformation(transformation_id)
        if not transformation:
            raise ValueError(f"Transformation with ID {transformation_id} does not exist")
        
        transformation.update_parameter(key, value)
        return self._storage.update_data_transformation(transformation)
    
    # Task-Dataset link operations
    
    def link_task_to_dataset_version(
        self,
        task_id: UUID,
        version_id: UUID,
        usage_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> UUID:
        """
        Link a task to a dataset version.
        
        Args:
            task_id: The ID of the task
            version_id: The ID of the dataset version
            usage_type: How the dataset is used (input, output, reference, etc.)
            description: Description of the relationship
            
        Returns:
            UUID: The ID of the created link
            
        Raises:
            ValueError: If version doesn't exist
        """
        version = self._storage.get_dataset_version(version_id)
        if not version:
            raise ValueError(f"Dataset version with ID {version_id} does not exist")
        
        # Check if link already exists
        existing_versions = self._storage.get_dataset_versions_for_task(task_id)
        for v in existing_versions:
            if v.id == version_id:
                # Link already exists
                return UUID('00000000-0000-0000-0000-000000000000')
        
        # Create the link
        link = TaskDatasetLink(
            task_id=task_id,
            dataset_version_id=version_id,
            usage_type=usage_type,
            description=description,
        )
        
        return self._storage.create_task_dataset_link(link)
    
    def unlink_task_from_dataset_version(self, task_id: UUID, version_id: UUID) -> bool:
        """
        Remove a link between a task and a dataset version.
        
        Args:
            task_id: The ID of the task
            version_id: The ID of the dataset version
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Find the link
        links = [
            link_id for link_id, link in self._storage._task_dataset_links.items()
            if link.task_id == task_id and link.dataset_version_id == version_id
        ]
        
        if not links:
            return False
        
        # Delete the link
        return self._storage.delete_task_dataset_link(links[0])
    
    def get_dataset_versions_for_task(self, task_id: UUID) -> List[DatasetVersion]:
        """
        Get all dataset versions associated with a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            List[DatasetVersion]: List of associated dataset versions
        """
        return self._storage.get_dataset_versions_for_task(task_id)
    
    def get_tasks_for_dataset_version(self, version_id: UUID) -> List[UUID]:
        """
        Get all task IDs associated with a dataset version.
        
        Args:
            version_id: The ID of the dataset version
            
        Returns:
            List[UUID]: List of associated task IDs
        """
        return self._storage.get_tasks_for_dataset_version(version_id)
    
    def add_note_to_link(self, task_id: UUID, version_id: UUID, note: str) -> bool:
        """
        Add a note to the link between a task and a dataset version.
        
        Args:
            task_id: The ID of the task
            version_id: The ID of the dataset version
            note: The note to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Find the link
        links = [
            link for link_id, link in self._storage._task_dataset_links.items()
            if link.task_id == task_id and link.dataset_version_id == version_id
        ]
        
        if not links:
            return False
        
        link = links[0]
        link.add_note(note)
        return self._storage.update_task_dataset_link(link)
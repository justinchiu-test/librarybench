# Unified Library Refactoring Plan

This document outlines the architectural design and implementation plan for the unified command-line task manager library that has been shared across all persona implementations.

## Analysis of Common Patterns

After analyzing both the ResearchTrack and SecureTask implementations, we identified several common patterns and functionality that have been moved to a shared library:

### 1. Data Models and Base Classes

Both implementations use Pydantic BaseModel for:
- Entity creation with UUIDs
- Status tracking
- Timestamps (created_at, updated_at)
- Tags
- Custom metadata management
- Parent-child relationships
- Note management

### 2. Storage Layer

Both implementations have:
- Repository/Storage patterns with CRUD operations
- Filtering and query capabilities
- In-memory implementations for testing
- Similar interface definitions
- File storage with optional encryption

### 3. Service Layer

Both implementations have:
- Service layers that wrap storage
- Validation logic
- Business logic separated from data models
- Association management between entities

### 4. Utility Functions

Common utilities across both implementations:
- Validation helper functions
- Data manipulation utilities
- Security and cryptography functions

## Implementation Details

### 1. Common Library Structure

The common library has been organized in the following structure:

```
common/
├── core/
│   ├── __init__.py
│   ├── models.py            # Base models and common data structures
│   ├── storage.py           # Storage interface and common implementations
│   ├── service.py           # Service base classes
│   ├── security.py          # Security-related functionality
│   └── utils.py             # Shared utility functions
```

### 2. Base Models Implementation (`models.py`)

Core models implemented as base classes for persona-specific implementations:

```python
# Base entity with shared fields
class BaseEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update(self, **kwargs) -> None:
        """
        Update entity fields with the provided values.
        
        Args:
            **kwargs: Field-value pairs to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

# Common task model with shared fields
class BaseTask(BaseEntity):
    title: str
    description: str
    status: str
    priority: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Organizational attributes
    tags: Set[str] = Field(default_factory=set)
    notes: List[str] = Field(default_factory=list)
    
    # Task relationships
    parent_id: Optional[str] = None
    subtask_ids: Set[str] = Field(default_factory=set)
    
    # Custom metadata for extensibility
    custom_metadata: Dict[str, Union[str, int, float, bool, list, dict]] = Field(
        default_factory=dict
    )
```

### 3. Storage Interfaces Implementation (`storage.py`)

We implemented the following storage interfaces:

1. **BaseStorageInterface**: Generic storage interface for all entities
2. **InMemoryStorage**: In-memory implementation of the storage interface
3. **BaseTaskStorageInterface**: Specialized interface for task entities
4. **InMemoryTaskStorage**: In-memory implementation of task storage
5. **FilePersistentStorage**: File-based storage with optional encryption
6. **FileTaskStorage**: File-based implementation of task storage

The FilePersistentStorage class can be used with or without encryption, making it suitable for both regular and security-sensitive data.

### 4. Service Layer Implementation (`service.py`)

We implemented the following service abstractions:

1. **BaseService**: Generic service for entity management
2. **BaseTaskService**: Specialized service for task management

These services provide common functionality for validator registration, CRUD operations, and task-specific methods like adding tags and notes.

### 5. Security Implementation (`security.py`)

For security-related functionality, we implemented:

1. **CryptoManager**: Manages cryptographic operations for secure data handling
2. **SecureStorageWrapper**: Wrapper for adding encryption to storage systems

### 6. Utilities Implementation (`utils.py`)

Common utility functions have been implemented in the following classes:

1. **ValidationHelper**: Validation utilities for data handling
2. **TimeUtils**: Date and time utilities
3. **IDGenerator**: Utilities for generating and handling IDs
4. **FileUtils**: File-related utilities
5. **JsonUtils**: JSON handling utilities

## Refactoring of Persona Implementations

### 1. ResearchTrack Refactoring

The ResearchTrack persona implementation has been refactored as follows:

1. **Models**: 
   - `ResearchQuestion` now extends `BaseEntity`
   - `ResearchTask` now extends `BaseTask`

2. **Storage**: 
   - Created `ResearchQuestionStorage` for managing research questions
   - Enhanced `InMemoryTaskStorage` to delegate to `ResearchQuestionStorage`
   - Refactored `TaskStorageInterface` to use common functionality

3. **Service**: 
   - `TaskManagementService` now extends `BaseTaskService`
   - Preserved specialized functionality for research-specific operations

### 2. SecureTask Refactoring

The SecureTask persona implementation has been refactored as follows:

1. **Models**: 
   - `Finding` now extends `BaseTask`

2. **Storage**: 
   - Refactored `FindingRepository` to use `FilePersistentStorage` with encryption
   - Preserved special handling of filters like 'severity'

## Testing Results

Tests were executed to verify that the refactored code maintains the same functionality. The test report confirms that both persona implementations continue to work as expected with the unified library.

## Performance Considerations

The refactoring maintains or improves performance by:

1. Reducing code duplication through shared components
2. Ensuring efficient storage operations with both in-memory and file-based options
3. Providing consistent security mechanisms with the CryptoManager
4. Supporting both encrypted and non-encrypted storage options

## Conclusion

The unified library successfully reduces code duplication while preserving the specialized functionality needed by each persona. By providing robust base classes and interfaces, we've enabled consistent patterns across implementations while allowing for domain-specific extensions.

The result is a more maintainable codebase that supports:
- Both researcher and security analyst personas
- Consistent data models and storage patterns
- Secure data handling for sensitive information
- Extensibility for future enhancements

## Integration Strategy
- Original package names are preserved, so existing tests work without modification
- Common functionality is moved to the common package
- Both persona implementations now use the common package
- Persona-specific extensions continue to live in their original packages
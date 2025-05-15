# Unified Library Refactoring Plan

This document outlines the architectural design and implementation plan for the unified command-line task manager library that will be shared across all persona implementations.

## Analysis of Common Patterns

After analyzing both the ResearchTrack and SecureTask implementations, we've identified several common patterns and functionality that can be moved to a shared library:

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

## Architectural Design for Common Library

### Overview

The common library will be organized in the following structure:

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

### Core Components and Responsibilities

#### 1. Base Models (`models.py`)

Core models that will be used as base classes for persona-specific implementations:

```python
# Base entity with shared fields
class BaseEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update(self, **kwargs) -> None:
        """Common update method for all entities"""
        # Implementation

# Common task model with shared fields
class BaseTask(BaseEntity):
    title: str
    description: str
    status: str
    priority: str
    tags: Set[str] = Field(default_factory=set)
    notes: List[str] = Field(default_factory=list)
    parent_id: Optional[UUID] = None
    
    # Common methods for tags, notes, status updates

# Common status enums
class TaskStatusEnum(str, Enum):
    """Base status values shared across implementations"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class TaskPriorityEnum(str, Enum):
    """Base priority values shared across implementations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

#### 2. Storage Interface (`storage.py`)

Common storage patterns and interfaces:

```python
class BaseStorageInterface(ABC):
    """Base storage interface for all repositories"""
    @abstractmethod
    def create(self, entity) -> UUID:
        pass
    
    @abstractmethod
    def get(self, entity_id: UUID):
        pass
    
    @abstractmethod
    def update(self, entity) -> bool:
        pass
    
    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        pass
    
    @abstractmethod
    def list(self, filters=None, **kwargs) -> List:
        pass

class InMemoryStorage(BaseStorageInterface):
    """Common in-memory implementation for testing"""
    # Implementation
```

#### 3. Service Layer (`service.py`)

Common service layer patterns:

```python
class BaseService:
    """Base service with common functionality"""
    def __init__(self, storage: BaseStorageInterface):
        self._storage = storage
    
    # Common validation methods
    # Common CRUD operations
```

#### 4. Security Module (`security.py`)

Common security functionality:

```python
class CryptoManager:
    """Shared cryptography utilities"""
    # Encryption/decryption
    # Hashing
    # Key generation
```

#### 5. Utilities (`utils.py`)

Common utility functions:

```python
class ValidationHelper:
    """Common validation utilities"""

class TimeUtils:
    """Date/time utilities"""

class IDGenerator:
    """UUID generation utilities"""
```

### Interface Definitions and Abstractions

The common library will define clear interfaces through:

1. Abstract Base Classes (ABCs) that define required methods
2. Pydantic models that define required fields
3. Type hints to ensure consistent usage
4. Extensive docstrings explaining usage patterns

### Extension Points

The design includes the following extension points for persona-specific functionality:

1. Model inheritance (e.g., ResearchTask extends BaseTask)
2. Service composition for specialized functionality
3. Custom field extensions on base models
4. Strategy pattern for pluggable behavior

### Component Relationships

- Base models serve as parents for persona-specific models
- Storage interfaces are implemented by persona-specific repositories
- Service layer orchestrates interactions between components
- Utilities provide common functionality to all components

## Migration Strategy

### ResearchTrack

1. **Models**:
   - Refactor `ResearchTask` to extend `BaseTask`
   - Refactor `ResearchQuestion` to extend `BaseEntity`
   - Maintain specialized fields and methods specific to research

2. **Storage**:
   - Refactor `TaskStorageInterface` to implement `BaseStorageInterface`
   - Reuse common in-memory implementation where possible

3. **Service**:
   - Refactor `TaskManagementService` to extend `BaseService`
   - Keep research-specific business logic

### SecureTask

1. **Models**:
   - Refactor `Finding` to extend `BaseTask`
   - Customize validators and methods for security context

2. **Repositories**:
   - Refactor `FindingRepository` to implement `BaseStorageInterface`
   - Keep security-specific storage mechanisms

3. **Security**:
   - Move common crypto functionality to shared `security.py`
   - Maintain security-specific extensions

## Implementation Order

1. Create core base models and interfaces
2. Implement utility functions
3. Develop storage interfaces and basic implementations
4. Create service layer abstractions
5. Implement security components
6. Refactor ResearchTrack to use common library
7. Refactor SecureTask to use common library
8. Run tests to ensure both implementations work correctly

## Testing Strategy

Our testing approach will be:

1. Develop unit tests for the common library components
2. Ensure all existing tests still pass after refactoring
3. Add integration tests to verify compatibility
4. Implement performance benchmarks to compare before/after
5. Create documentation and examples for each component

## Performance Considerations

The refactoring will focus on:
1. Maintaining or improving current performance
2. Reducing memory usage through shared code
3. Ensuring crypto operations remain efficient
4. Optimizing storage patterns for better scaling

## Conclusion

This unified library will significantly reduce code duplication while maintaining the specialized functionality needed by each persona. By providing robust base classes and interfaces, we'll enable consistent patterns across implementations while allowing for domain-specific extensions.

## Integration Strategy
- Original package names are preserved, so existing tests work without modification
- Common functionality is moved to the common package
- New code can directly use the common package
- Persona-specific extensions continue to live in their original packages
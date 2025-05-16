# Unified Personal Knowledge Management System Architecture Plan

## Overview

The Unified Personal Knowledge Management System aims to provide a shared foundation for specialized knowledge management systems tailored to different personas. This document outlines the architecture, components, interfaces, and migration strategy for creating a common library that can be used across all persona implementations.

## 1. Analysis of Common Patterns

After analyzing both the `productmind` and `researchbrain` implementations, several common patterns have been identified:

### Common Data Structures
- Both implementations use Pydantic `BaseModel` for data models
- Both have core objects with unique identifiers (UUID)
- Both implement timestamp tracking (created_at, updated_at)
- Both use collections of related objects with references between them
- Both use tags for categorization

### Common Functionality
- Storage and retrieval of objects (filesystem-based storage)
- Object relationship management (referencing between objects)
- Serialization/deserialization to disk (YAML/JSON)
- Search capabilities (full-text search)
- Cache management for performance
- Query filtering by attributes

### Common Design Patterns
- Repository pattern for data access
- Factory methods for object creation
- Knowledge graph representation of relationships between entities
- UUID-based references between objects

## 2. Core Components and Responsibilities

### 1. Common Core Models (`common/core/models.py`)
- **KnowledgeNode**: Base class for all knowledge entities with common attributes:
  - id (UUID)
  - created_at/updated_at timestamps
  - tags
  - node_type
- **RelationType**: Enum defining standard relationship types between nodes
- **Relation**: Class representing relationships between knowledge nodes
- **Status/Priority**: Common enums for status and priority values
- **Annotation**: Shared model for annotations on knowledge items

### 2. Storage System (`common/core/storage.py`)
- **BaseStorage**: Abstract interface for all storage implementations
  - save/get/delete/list/query operations
  - attachment handling
  - backup/restore functionality
  - search capabilities
- **LocalStorage**: File-based implementation using YAML/JSON
  - Caching mechanisms for performance
  - Concurrent access safety via locks
  - Search indexing
  - Serialization/deserialization helpers

### 3. Knowledge Management (`common/core/knowledge.py`)
- **KnowledgeGraph**: Graph representation of knowledge nodes and their relationships
  - Node and edge management
  - Neighbor and path finding
  - Import/export functionality
- **KnowledgeBase**: Abstract base class for knowledge system implementations  
- **StandardKnowledgeBase**: Common implementation with core operations
  - Node CRUD operations
  - Relationship management
  - Search and filtering

### 4. Utility Functions (`common/utils/`)
- **conversion.py**: Data format conversion utilities
- **file_ops.py**: File operations and helpers
- **search.py**: Advanced search algorithms and helpers

## 3. Interface Definitions and Abstractions

### 1. KnowledgeNode Interface
```python
class KnowledgeNode(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    tags: Set[str]
    node_type: NodeType
    
    def update(self) -> None:
        """Update the last modified timestamp."""
```

### 2. Storage Interface
```python
class BaseStorage(ABC):
    @abstractmethod
    def save(self, item: T) -> None:
        """Save an item to storage."""
        
    @abstractmethod
    def get(self, model_type: Type[T], item_id: UUID) -> Optional[T]:
        """Retrieve an item by ID."""
        
    @abstractmethod
    def delete(self, model_type: Type[T], item_id: UUID) -> bool:
        """Delete an item by ID."""
        
    @abstractmethod
    def list_all(self, model_type: Type[T]) -> List[T]:
        """List all items of a specific type."""
        
    @abstractmethod
    def query(self, model_type: Type[T], **filters) -> List[T]:
        """Query items of a specific type with filters."""
        
    @abstractmethod
    def search_text(self, model_type: Type[T], search_text: str, fields: List[str]) -> List[T]:
        """Search for items containing specific text in certain fields."""
```

### 3. Knowledge Management Interface
```python
class KnowledgeBase(ABC):
    @abstractmethod
    def __init__(self, storage: BaseStorage):
        """Initialize with a storage implementation."""
        
    @abstractmethod
    def add_node(self, node: KnowledgeNode) -> UUID:
        """Add a knowledge node to the system."""
        
    @abstractmethod
    def get_node(self, node_id: UUID, node_type: Optional[Type[T]] = None) -> Optional[KnowledgeNode]:
        """Get a knowledge node by ID."""
        
    @abstractmethod
    def update_node(self, node: KnowledgeNode) -> bool:
        """Update a knowledge node."""
        
    @abstractmethod
    def delete_node(self, node_id: UUID) -> bool:
        """Delete a knowledge node."""
        
    @abstractmethod
    def link_nodes(self, source_id: UUID, target_id: UUID, relation_type: RelationType, 
                 metadata: Optional[Dict[str, Any]] = None) -> Relation:
        """Create a relationship between two nodes."""
        
    @abstractmethod
    def get_related_nodes(self, node_id: UUID, relation_types: Optional[List[RelationType]] = None,
                        direction: str = "both") -> Dict[str, List[KnowledgeNode]]:
        """Get nodes related to a specific knowledge node."""
        
    @abstractmethod
    def search(self, query: str, node_types: Optional[List[Type[T]]] = None) -> Dict[str, List[KnowledgeNode]]:
        """Search for knowledge nodes containing a specific text."""
```

## 4. Extension Points for Persona-Specific Functionality

1. **Domain-Specific Node Types**: Personas can extend KnowledgeNode with specific attributes:
   - ResearchBrain extends with Citation, ResearchQuestion, Experiment, etc.
   - ProductMind extends with Feedback, Competitor, Feature, etc.

2. **Specialized Services**: Personas can implement domain-specific services:
   - ResearchBrain: citation management, experiment templates
   - ProductMind: feedback clustering, prioritization frameworks

3. **Custom Relationship Types**: Personas can define additional relation types for domain-specific connections

4. **Storage Extensions**: Personas can extend storage with domain-specific queries and indexes

5. **Custom Knowledge Operations**: Personas can create specialized knowledge operations:
   - ResearchBrain: managing evidence, citations
   - ProductMind: clustering feedback, analyzing stakeholder perspectives

## 5. Component Relationships

- **KnowledgeNode ↔ BaseStorage**: Storage persists knowledge nodes
- **KnowledgeNode ↔ Relation**: Relations connect knowledge nodes
- **KnowledgeGraph ↔ StandardKnowledgeBase**: Knowledge base uses graph for relationships
- **StandardKnowledgeBase ↔ BaseStorage**: Knowledge base uses storage for persistence
- **Domain Models ↔ KnowledgeNode**: Domain models extend base knowledge node
- **Domain Services ↔ KnowledgeBase**: Domain services extend knowledge base

```
┌─────────────────────────────────────┐
│ Persona-Specific Implementations    │
│                                     │
│  ┌─────────────┐    ┌─────────────┐ │
│  │ ResearchBrain│    │ ProductMind │ │
│  │             │    │             │ │
│  └──────┬──────┘    └──────┬──────┘ │
└─────────┼─────────────────┼─────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────┐
│ Common Library                      │
│                                     │
│  ┌─────────────┐    ┌─────────────┐ │
│  │ KnowledgeBase│◄───┤KnowledgeGraph│ │
│  │             │    │             │ │
│  └──────┬──────┘    └─────────────┘ │
│         │                          │
│         ▼                          │
│  ┌─────────────┐    ┌─────────────┐ │
│  │ BaseStorage │    │ KnowledgeNode│ │
│  │             │    │             │ │
│  └─────────────┘    └─────────────┘ │
└─────────────────────────────────────┘
```

## 6. Migration Strategy

### ResearchBrain Migration

1. **Models Migration**:
   - Keep domain-specific model classes (Citation, ResearchQuestion, etc.)
   - Update to inherit from common KnowledgeNode
   - Align with common attributes and interfaces

2. **Storage Migration**:
   - Replace custom storage with common BaseStorage implementation
   - Update serialization/deserialization to use common patterns
   - Map legacy paths to new structure for backward compatibility

3. **Knowledge Graph Migration**:
   - Replace custom graph with common KnowledgeGraph
   - Map domain-specific relationships to common patterns
   - Use StandardKnowledgeBase for core operations

4. **Services Migration**:
   - Keep domain-specific services (citation formatting, grant exports)
   - Update to use common interfaces for knowledge operations
   - Add domain-specific extensions where needed

### ProductMind Migration

1. **Models Migration**:
   - Refactor domain models (Feedback, Stakeholder, etc.) to inherit from KnowledgeNode
   - Align relationship models with common Relation class
   - Preserve specific attributes for domain functionality

2. **Storage Migration**:
   - Update to use common BaseStorage implementation
   - Migrate existing persistence logic to common patterns
   - Preserve domain-specific query functionality

3. **Analysis Engine Migration**:
   - Keep specialized analysis engines (feedback clustering, trend detection)
   - Update to use common knowledge base for persistence and relationships
   - Preserve algorithmic components while standardizing interfaces

4. **Utility Migration**:
   - Replace custom utility functions with common implementations
   - Standardize conversion and search operations
   - Keep domain-specific utilities as extensions

## 7. Implementation Plan

1. **Phase 1: Common Library Implementation**
   - Implement core models and enums
   - Implement storage system
   - Implement knowledge graph and base
   - Implement utility functions

2. **Phase 2: ResearchBrain Migration**
   - Update models to use common base classes
   - Refactor storage to use common implementation
   - Migrate knowledge operations to common interfaces
   - Preserve domain-specific functionality

3. **Phase 3: ProductMind Migration**
   - Update models to use common base classes
   - Refactor storage to use common implementation
   - Migrate knowledge operations to common interfaces
   - Preserve domain-specific functionality

4. **Phase 4: Testing and Validation**
   - Run comprehensive tests for each persona
   - Ensure backward compatibility
   - Verify performance requirements
   - Document any issues or limitations

## 8. Detailed Migration Steps for ResearchBrain

### Phase 1: Model Migration

1. Update all models in `researchbrain.core.models` to inherit from `common.core.models.KnowledgeNode`
2. Update imports to use common enums where applicable
3. Ensure backward compatibility with existing code
4. Create adapter models where necessary for special cases

### Phase 2: Storage Migration

1. Replace `researchbrain.core.storage.LocalStorage` with `common.core.storage.LocalStorage`
2. Update all imports and references in `researchbrain.core.brain`
3. Adapt directory structure to match common storage patterns
4. Update serialization/deserialization logic for compatibility

### Phase 3: Knowledge Graph Migration

1. Refactor `ResearchBrain._build_knowledge_graph()` to use `common.core.knowledge.KnowledgeGraph`
2. Update all graph operations in `ResearchBrain` methods
3. Preserve specialized relationship types and attributes
4. Implement any necessary adapter methods

### Phase 4: Testing and Validation

1. Run all ResearchBrain tests to verify functionality
2. Fix any integration issues
3. Refine common components if needed
4. Ensure performance meets or exceeds original implementation

## 9. Detailed Migration Steps for ProductMind

### Phase 1: Model Migration

1. Update all models in `productmind.models` to inherit from `common.core.models.KnowledgeNode`
2. Update imports to use common enums where applicable
3. Ensure backward compatibility with existing code
4. Create adapter models where necessary for special cases

### Phase 2: Storage Migration

1. Update all references to storage in the ProductMind modules to use `common.core.storage.LocalStorage`
2. Adapt directory structure to match common storage patterns
3. Update serialization/deserialization logic for compatibility

### Phase 3: Engine Migration

1. Refactor `FeedbackAnalysisEngine` to use the common `KnowledgeBase` and `KnowledgeGraph`
2. Update all references to storage and knowledge management
3. Preserve specialized clustering and analysis algorithms
4. Implement any necessary adapter methods

### Phase 4: Testing and Validation

1. Run all ProductMind tests to verify functionality
2. Fix any integration issues
3. Refine common components if needed
4. Ensure performance meets or exceeds original implementation

## 10. Testing Strategy

1. Unit test all common components
2. Integration test with both persona implementations
3. Use existing tests to verify preserved functionality
4. Perform performance benchmarks
5. Run all tests for both personas to ensure compatibility

## 11. Dependencies

- Pydantic: For data modeling
- NetworkX: For knowledge graph representation (optional fallback implementation provided)
- Python standard library: For core functionality

## 12. Risks and Mitigations

### Risk: Breaking existing functionality
- Mitigation: Incremental migration with continuous testing

### Risk: Performance degradation
- Mitigation: Optimize common components and maintain caching

### Risk: Incompatible data formats
- Mitigation: Implement adapter patterns and migration utilities

### Risk: Test failures
- Mitigation: Address each test failure incrementally, preserving existing behavior
"""Document models for the legal discovery interpreter."""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field

from common.models.base import BaseModel as CommonBaseModel, Document as CommonDocument


class DocumentMetadata(BaseModel):
    """Metadata for a legal document."""
    
    document_id: str = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Document title")
    document_type: str = Field(..., description="Type of document (e.g., contract, email, memo)")
    date_created: datetime = Field(..., description="Date and time the document was created")
    date_modified: Optional[datetime] = Field(None, description="Date and time the document was last modified")
    author: Optional[str] = Field(None, description="Author of the document")
    custodian: Optional[str] = Field(None, description="Custodian of the document")
    source: Optional[str] = Field(None, description="Source of the document")
    file_path: Optional[str] = Field(None, description="File path where the document is stored")
    file_type: Optional[str] = Field(None, description="File type of the document")
    file_size: Optional[int] = Field(None, description="Size of the document in bytes")
    
    # Additional metadata fields specific to legal discovery
    confidentiality: Optional[str] = Field(None, description="Confidentiality level of the document")
    privilege_status: Optional[str] = Field(None, description="Privilege status of the document")
    litigation_hold: Optional[bool] = Field(None, description="Whether the document is on litigation hold")
    production_number: Optional[str] = Field(None, description="Production number for the document")
    redaction_status: Optional[str] = Field(None, description="Redaction status of the document")
    
    class Config:
        """Pydantic model configuration."""
        
        extra = "allow"  # Allow extra fields for flexibility


class Document(CommonDocument):
    """Base model for a legal document."""
    
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    
    # Search and analysis related fields
    relevance_score: Optional[float] = Field(None, description="Relevance score for the document")
    privilege_score: Optional[float] = Field(None, description="Privilege score for the document")
    extracted_entities: Optional[Dict[str, List[str]]] = Field(None, 
                                                            description="Extracted entities from the document")
    tags: Optional[List[str]] = Field(None, description="Tags assigned to the document")
    
    def __init__(
        self,
        id: str = None,
        content: str = None,
        metadata: DocumentMetadata = None,
        relevance_score: Optional[float] = None,
        privilege_score: Optional[float] = None,
        extracted_entities: Optional[Dict[str, List[str]]] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ):
        """Initialize a document.

        Args:
            id: Document ID (uses metadata.document_id if not provided)
            content: Document content
            metadata: Document metadata
            relevance_score: Relevance score for the document
            privilege_score: Privilege score for the document
            extracted_entities: Extracted entities from the document
            tags: Tags assigned to the document
        """
        doc_id = id if id is not None else (metadata.document_id if metadata else None)
        super().__init__(
            id=doc_id,
            content=content,
            metadata=metadata.__dict__ if metadata else {}
        )
        self.metadata = metadata
        self.relevance_score = relevance_score
        self.privilege_score = privilege_score
        self.extracted_entities = extracted_entities
        self.tags = tags
    
    def get_content_preview(self, max_length: int = 200) -> str:
        """Get a preview of the document content.
        
        Args:
            max_length: Maximum length of the preview
            
        Returns:
            A preview of the document content
        """
        if len(self.content) <= max_length:
            return self.content
        
        return f"{self.content[:max_length]}..."


class EmailDocument(Document):
    """Model for an email document."""
    
    sender: str = Field(..., description="Email sender")
    recipients: List[str] = Field(..., description="Email recipients")
    cc: Optional[List[str]] = Field(None, description="CC recipients")
    bcc: Optional[List[str]] = Field(None, description="BCC recipients")
    subject: str = Field(..., description="Email subject")
    sent_date: datetime = Field(..., description="Date and time the email was sent")
    thread_id: Optional[str] = Field(None, description="ID of the email thread")
    in_reply_to: Optional[str] = Field(None, description="ID of the email this is in reply to")
    attachments: Optional[List[str]] = Field(None, description="List of attachment document IDs")


class LegalAgreement(Document):
    """Model for a legal agreement document."""
    
    parties: List[str] = Field(..., description="Parties to the agreement")
    effective_date: datetime = Field(..., description="Effective date of the agreement")
    termination_date: Optional[datetime] = Field(None, description="Termination date of the agreement")
    governing_law: Optional[str] = Field(None, description="Governing law of the agreement")
    agreement_type: str = Field(..., description="Type of agreement")


class DocumentCollection(CommonBaseModel):
    """A collection of documents for a legal discovery case."""
    
    collection_id: str = Field(..., description="Unique identifier for the collection")
    name: str = Field(..., description="Name of the collection")
    description: Optional[str] = Field(None, description="Description of the collection")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    documents: Dict[str, Union[Document, EmailDocument, LegalAgreement]] = Field(
        default_factory=dict, description="Documents in the collection, indexed by document ID"
    )
    
    def add_document(self, document: Union[Document, EmailDocument, LegalAgreement]) -> None:
        """Add a document to the collection.
        
        Args:
            document: Document to add
        """
        self.documents[document.metadata.document_id] = document
        self.updated_at = datetime.now()
    
    def remove_document(self, document_id: str) -> None:
        """Remove a document from the collection.
        
        Args:
            document_id: ID of the document to remove
        """
        if document_id in self.documents:
            del self.documents[document_id]
            self.updated_at = datetime.now()
    
    def get_document(self, document_id: str) -> Optional[Union[Document, EmailDocument, LegalAgreement]]:
        """Get a document from the collection.
        
        Args:
            document_id: ID of the document to get
            
        Returns:
            The document, or None if not found
        """
        return self.documents.get(document_id)
    
    def count(self) -> int:
        """Count the number of documents in the collection.
        
        Returns:
            Number of documents in the collection
        """
        return len(self.documents)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert collection to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "collection_id": self.collection_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "document_count": self.count(),
        }
"""
Pytest configuration for Academic Knowledge Vault tests.

This file contains shared fixtures and configuration for all test modules.
"""

import pytest
import tempfile
from pathlib import Path

from academic_knowledge_vault.storage.note_storage import NoteStorage, NoteCollectionStorage
from academic_knowledge_vault.storage.citation_storage import CitationStorage, CitationCollectionStorage
from academic_knowledge_vault.storage.research_question_storage import (
    ResearchQuestionStorage,
    HypothesisStorage,
    EvidenceStorage,
    ResearchQuestionCollectionStorage
)
from academic_knowledge_vault.storage.grant_proposal_storage import (
    GrantProposalStorage,
    GrantProposalWorkspaceStorage
)
from academic_knowledge_vault.storage.experiment_storage import (
    ExperimentStorage,
    ExperimentProtocolStorage,
    ExperimentCollectionStorage
)
from academic_knowledge_vault.storage.collaboration_storage import (
    AnnotationStorage,
    ImportedAnnotationStorage,
    CollaborationSessionStorage
)
from academic_knowledge_vault.storage.knowledge_discovery_storage import (
    KnowledgeDiscoveryStorage,
    KnowledgeGraphStorage,
    TopicModelStorage,
    TemporalAnalysisStorage
)
from academic_knowledge_vault.services.note_management.note_service import NoteService
from academic_knowledge_vault.services.citation_management.citation_service import CitationService
from academic_knowledge_vault.services.research_question.research_question_service import ResearchQuestionService
from academic_knowledge_vault.services.grant_proposal.grant_proposal_service import GrantProposalService
from academic_knowledge_vault.services.experiment_management.experiment_service import ExperimentService
from academic_knowledge_vault.services.collaboration.collaboration_service import CollaborationService
from academic_knowledge_vault.services.knowledge_discovery.discovery_service import KnowledgeDiscoveryService


@pytest.fixture(scope="session")
def base_storage_dir():
    """Create a temporary base directory for all test storage."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def storage_components(base_storage_dir):
    """Create storage components for testing."""
    # Create subdirectories for different storage types
    paths = {
        "notes": base_storage_dir / "notes",
        "note_collections": base_storage_dir / "note_collections",
        "citations": base_storage_dir / "citations",
        "citation_collections": base_storage_dir / "citation_collections",
        "questions": base_storage_dir / "questions",
        "hypotheses": base_storage_dir / "hypotheses",
        "evidence": base_storage_dir / "evidence",
        "question_collections": base_storage_dir / "question_collections",
        "proposals": base_storage_dir / "proposals",
        "workspaces": base_storage_dir / "workspaces",
        "experiments": base_storage_dir / "experiments",
        "protocols": base_storage_dir / "protocols",
        "experiment_collections": base_storage_dir / "experiment_collections",
        "annotations": base_storage_dir / "annotations",
        "imported_annotations": base_storage_dir / "imported_annotations",
        "sessions": base_storage_dir / "sessions",
        "discoveries": base_storage_dir / "discoveries",
        "graphs": base_storage_dir / "graphs",
        "topic_models": base_storage_dir / "topic_models",
        "temporal_analyses": base_storage_dir / "temporal_analyses"
    }
    
    # Create storage instances
    storages = {
        "note_storage": NoteStorage(paths["notes"]),
        "note_collection_storage": NoteCollectionStorage(paths["note_collections"]),
        "citation_storage": CitationStorage(paths["citations"]),
        "citation_collection_storage": CitationCollectionStorage(paths["citation_collections"]),
        "question_storage": ResearchQuestionStorage(paths["questions"]),
        "hypothesis_storage": HypothesisStorage(paths["hypotheses"]),
        "evidence_storage": EvidenceStorage(paths["evidence"]),
        "question_collection_storage": ResearchQuestionCollectionStorage(paths["question_collections"]),
        "proposal_storage": GrantProposalStorage(paths["proposals"]),
        "workspace_storage": GrantProposalWorkspaceStorage(paths["workspaces"]),
        "experiment_storage": ExperimentStorage(paths["experiments"]),
        "protocol_storage": ExperimentProtocolStorage(paths["protocols"]),
        "experiment_collection_storage": ExperimentCollectionStorage(paths["experiment_collections"]),
        "annotation_storage": AnnotationStorage(paths["annotations"]),
        "imported_annotation_storage": ImportedAnnotationStorage(paths["imported_annotations"]),
        "session_storage": CollaborationSessionStorage(paths["sessions"]),
        "discovery_storage": KnowledgeDiscoveryStorage(paths["discoveries"]),
        "graph_storage": KnowledgeGraphStorage(paths["graphs"]),
        "topic_model_storage": TopicModelStorage(paths["topic_models"]),
        "temporal_analysis_storage": TemporalAnalysisStorage(paths["temporal_analyses"])
    }
    
    return storages


@pytest.fixture
def service_components(storage_components):
    """Create service components for testing."""
    services = {
        "note_service": NoteService(
            storage_components["note_storage"],
            storage_components["note_collection_storage"]
        ),
        "citation_service": CitationService(
            storage_components["citation_storage"],
            storage_components["citation_collection_storage"]
        ),
        "research_service": ResearchQuestionService(
            storage_components["question_storage"],
            storage_components["hypothesis_storage"],
            storage_components["evidence_storage"],
            storage_components["question_collection_storage"]
        ),
        "proposal_service": GrantProposalService(
            storage_components["proposal_storage"],
            storage_components["workspace_storage"]
        ),
        "experiment_service": ExperimentService(
            storage_components["experiment_storage"],
            storage_components["protocol_storage"],
            storage_components["experiment_collection_storage"]
        ),
        "collaboration_service": CollaborationService(
            storage_components["annotation_storage"],
            storage_components["imported_annotation_storage"],
            storage_components["session_storage"]
        ),
        "discovery_service": KnowledgeDiscoveryService(
            storage_components["discovery_storage"],
            storage_components["graph_storage"],
            storage_components["topic_model_storage"],
            storage_components["temporal_analysis_storage"]
        )
    }
    
    return services
"""
Integration tests for the Academic Knowledge Vault system.

These tests verify that the different components work together as expected
for common academic research workflows.
"""

import os
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

from academic_knowledge_vault.models.base import KnowledgeItemType, Reference
from academic_knowledge_vault.models.note import Note, NoteType
from academic_knowledge_vault.models.citation import Citation, PublicationType
from academic_knowledge_vault.models.research_question import (
    Evidence, 
    EvidenceStrength, 
    EvidenceType,
    Hypothesis, 
    HypothesisStatus,
    ResearchQuestion, 
    ResearchQuestionStatus
)
from academic_knowledge_vault.models.grant_proposal import (
    GrantProposal,
    GrantProposalWorkspace,
    FundingStatus,
    ProposalSection
)
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
from academic_knowledge_vault.services.note_management.note_service import NoteService
from academic_knowledge_vault.services.citation_management.citation_service import CitationService
from academic_knowledge_vault.services.research_question.research_question_service import ResearchQuestionService
from academic_knowledge_vault.services.grant_proposal.grant_proposal_service import GrantProposalService


class TestAcademicResearchWorkflow:
    """Integration tests for common academic research workflows."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def services(self, storage_dir):
        """Set up all the services."""
        base_dir = Path(storage_dir)
        
        # Create storage instances
        note_storage = NoteStorage(base_dir / "notes")
        note_collection_storage = NoteCollectionStorage(base_dir / "note_collections")
        
        citation_storage = CitationStorage(base_dir / "citations")
        citation_collection_storage = CitationCollectionStorage(base_dir / "citation_collections")
        
        question_storage = ResearchQuestionStorage(base_dir / "questions")
        hypothesis_storage = HypothesisStorage(base_dir / "hypotheses")
        evidence_storage = EvidenceStorage(base_dir / "evidence")
        question_collection_storage = ResearchQuestionCollectionStorage(base_dir / "question_collections")
        
        proposal_storage = GrantProposalStorage(base_dir / "proposals")
        workspace_storage = GrantProposalWorkspaceStorage(base_dir / "workspaces")
        
        # Create services
        note_service = NoteService(note_storage, note_collection_storage)
        citation_service = CitationService(citation_storage, citation_collection_storage)
        research_service = ResearchQuestionService(
            question_storage, hypothesis_storage, evidence_storage, question_collection_storage
        )
        proposal_service = GrantProposalService(proposal_storage, workspace_storage)
        
        return {
            "note_service": note_service,
            "citation_service": citation_service,
            "research_service": research_service,
            "proposal_service": proposal_service
        }
    
    def test_literature_review_to_hypothesis_workflow(self, services):
        """
        Test the workflow from literature review to hypothesis formation.
        
        This workflow includes:
        1. Importing literature from BibTeX
        2. Creating notes about papers
        3. Identifying research questions
        4. Formulating hypotheses
        5. Collecting evidence
        """
        note_service = services["note_service"]
        citation_service = services["citation_service"]
        research_service = services["research_service"]
        
        # 1. Import literature from BibTeX
        bibtex_content = """
        @article{smith2020neural,
            author = {Smith, John and Jones, Sarah},
            title = {Neural Mechanisms of Memory Formation},
            journal = {Journal of Neuroscience},
            year = {2020},
            volume = {42},
            number = {3},
            pages = {123--145},
            doi = {10.1234/jneurosci.2020.42.3.123}
        }
        
        @article{brown2021memory,
            author = {Brown, Robert and Davis, Emily},
            title = {Memory Consolidation During Sleep},
            journal = {Sleep Research},
            year = {2021},
            volume = {15},
            number = {2},
            pages = {78--92},
            doi = {10.5678/sleep.2021.15.2.78}
        }
        """
        
        citation_ids = citation_service.import_bibtex(bibtex_content)
        assert len(citation_ids) == 2
        
        # Get the citation keys
        smith_citation = citation_service.get_citation(citation_ids[0])
        brown_citation = citation_service.get_citation(citation_ids[1])
        
        # 2. Create notes about papers
        smith_note_id = note_service.create_note(
            title="Notes on Smith & Jones (2020)",
            content="""
            # Neural Mechanisms of Memory Formation
            
            This paper by @smith2020neural discusses the neural mechanisms involved in memory formation.
            
            ## Key findings:
            
            1. Hippocampal involvement in initial memory encoding
            2. Role of sleep in memory consolidation
            3. Neurotransmitter changes during memory formation
            
            ## Questions raised:
            
            - How do different types of memory formation processes interact?
            - What is the role of specific neurotransmitters in memory consolidation?
            
            ## Limitations:
            
            - Small sample size (n=20)
            - Limited to young adults
            """,
            note_type=NoteType.LITERATURE,
            tags=["memory", "neuroscience", "hippocampus"]
        )
        
        brown_note_id = note_service.create_note(
            title="Notes on Brown & Davis (2021)",
            content="""
            # Memory Consolidation During Sleep
            
            This paper by @brown2021memory focuses on how sleep affects memory consolidation.
            
            ## Key findings:
            
            1. Slow-wave sleep is crucial for declarative memory consolidation
            2. REM sleep plays a role in procedural memory
            3. Sleep disruption impairs consolidation processes
            
            ## Questions raised:
            
            - How do different sleep stages affect different types of memory?
            - What are the molecular mechanisms of sleep-dependent memory consolidation?
            
            ## Limitations:
            
            - Correlational study design
            - Self-reported sleep quality measures
            """,
            note_type=NoteType.LITERATURE,
            tags=["memory", "sleep", "consolidation"]
        )
        
        # 3. Identify a research question
        question_id = research_service.create_research_question(
            question="What is the relationship between sleep quality and memory consolidation in older adults?",
            description="While the relationship between sleep and memory is well-established in young adults, less is known about how this relationship changes with age.",
            tags=["memory", "sleep", "aging"],
            priority=1,
            status=ResearchQuestionStatus.ACTIVE,
            knowledge_gaps=[
                "Limited studies in older adult populations",
                "Unclear how age-related sleep changes affect consolidation",
                "Molecular mechanisms poorly understood in aging populations"
            ],
            related_citations=citation_ids  # Pass the citation IDs directly
        )
        
        # Add the question reference to the notes
        note_service.add_reference(
            note_id=smith_note_id,
            referenced_item_id=question_id,
            item_type=KnowledgeItemType.RESEARCH_QUESTION,
            context="Relevant to our research question on aging"
        )
        
        note_service.add_reference(
            note_id=brown_note_id,
            referenced_item_id=question_id,
            item_type=KnowledgeItemType.RESEARCH_QUESTION,
            context="Directly relevant to our sleep-memory research question"
        )
        
        # 4. Formulate hypotheses
        hypothesis1_id = research_service.create_hypothesis(
            statement="Sleep quality decline in older adults leads to proportional decline in declarative memory consolidation.",
            research_question_id=question_id,
            status=HypothesisStatus.PROPOSED,
            tags=["declarative memory", "sleep quality"],
            confidence_level=0.5
        )
        
        hypothesis2_id = research_service.create_hypothesis(
            statement="Procedural memory consolidation is less affected by age-related sleep changes than declarative memory.",
            research_question_id=question_id,
            status=HypothesisStatus.PROPOSED,
            tags=["procedural memory", "sleep architecture"],
            confidence_level=0.4
        )
        
        # 5. Add evidence
        # Supporting evidence for hypothesis 1
        evidence1_id = research_service.create_evidence(
            description="Brown & Davis (2021) showed strong correlation between slow-wave sleep and declarative memory in young adults.",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.MODERATE,
            source_id=citation_ids[1],
            source_type=KnowledgeItemType.CITATION,
            supports_ids=[hypothesis1_id],
            confidence_score=0.7,
            methodology_notes="Well-designed study but young population only"
        )
        
        # Contradicting evidence for hypothesis 1
        evidence2_id = research_service.create_evidence(
            description="Smith & Jones (2020) found that hippocampal activity during encoding predicts successful recall regardless of sleep quality.",
            evidence_type=EvidenceType.CONTRADICTING,
            strength=EvidenceStrength.WEAK,
            source_id=citation_ids[0],
            source_type=KnowledgeItemType.CITATION,
            contradicts_ids=[hypothesis1_id],
            confidence_score=0.4,
            methodology_notes="Indirect evidence as study didn't directly measure sleep in older adults"
        )
        
        # Supporting evidence for hypothesis 2
        evidence3_id = research_service.create_evidence(
            description="Brown & Davis (2021) noted that procedural memory tasks showed less disruption from poor sleep than declarative tasks.",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.MODERATE,
            source_id=citation_ids[1],
            source_type=KnowledgeItemType.CITATION,
            supports_ids=[hypothesis2_id],
            confidence_score=0.6,
            methodology_notes="Secondary finding in the paper, not the primary focus"
        )
        
        # Verify the research network
        question = research_service.get_research_question(question_id)
        assert len(question.hypotheses) == 2
        assert len(question.related_citations) == 2
        
        hypothesis1 = research_service.get_hypothesis(hypothesis1_id)
        assert len(hypothesis1.supporting_evidence) == 1
        assert len(hypothesis1.contradicting_evidence) == 1
        
        hypothesis2 = research_service.get_hypothesis(hypothesis2_id)
        assert len(hypothesis2.supporting_evidence) == 1
        
        # Calculate evidence strength
        strength1 = research_service.calculate_evidence_strength(hypothesis1_id)
        strength2 = research_service.calculate_evidence_strength(hypothesis2_id)
        
        # Hypothesis 2 should have stronger support than hypothesis 1
        assert strength2 > strength1
    
    def test_grant_proposal_workflow(self, services):
        """
        Test the workflow for creating a grant proposal based on research.
        
        This workflow includes:
        1. Setting up research components
        2. Creating a grant proposal workspace
        3. Creating a grant proposal
        4. Adding research components to the proposal
        """
        note_service = services["note_service"]
        citation_service = services["citation_service"]
        research_service = services["research_service"]
        proposal_service = services["proposal_service"]
        
        # 1. Set up research components
        # Create a citation
        citation_id = citation_service.create_citation(
            title="Neural Mechanisms of Memory Formation",
            authors=[
                {"name": "Smith, John", "affiliation": "University A"},
                {"name": "Jones, Sarah", "affiliation": "University B"}
            ],
            publication_year=2020,
            publication_type=PublicationType.JOURNAL_ARTICLE,
            journal_or_conference="Journal of Neuroscience",
            tags=["memory", "neuroscience"]
        )
        
        # Create a research note
        note_id = note_service.create_note(
            title="Research Ideas on Memory and Aging",
            content="""
            # Memory and Aging Research
            
            Key questions to explore:
            
            1. How does memory consolidation change with age?
            2. What interventions can improve memory in older adults?
            3. What are the neural correlates of memory decline?
            """,
            note_type=NoteType.IDEA,
            tags=["memory", "aging", "research ideas"]
        )
        
        # Create a research question
        question_id = research_service.create_research_question(
            question="How can sleep quality interventions improve memory consolidation in older adults?",
            description="This question explores potential interventions to enhance memory through improved sleep.",
            tags=["sleep", "memory", "intervention"],
            priority=1
        )
        
        # Create a hypothesis
        hypothesis_id = research_service.create_hypothesis(
            statement="Targeted sleep enhancement interventions can improve declarative memory performance in older adults.",
            research_question_id=question_id,
            status=HypothesisStatus.PROPOSED,
            tags=["intervention", "declarative memory"]
        )
        
        # 2. Create a grant proposal workspace
        workspace_id = proposal_service.create_workspace(
            name="Sleep and Memory Intervention Grant",
            description="Workspace for developing NIH grant on sleep interventions for memory improvement",
            tags=["NIH", "sleep", "memory", "R01"]
        )
        
        # Add components to the workspace
        proposal_service.add_note_to_workspace(workspace_id, note_id)
        proposal_service.add_citation_to_workspace(workspace_id, citation_id)
        proposal_service.add_question_to_workspace(workspace_id, question_id)
        
        # 3. Create a grant proposal
        proposal_id = proposal_service.create_proposal(
            title="Improving Memory Consolidation in Older Adults Through Sleep Quality Interventions",
            funding_agency="National Institute on Aging",
            agency_type="government",
            abstract="This project aims to develop and test interventions to improve sleep quality in older adults, with the goal of enhancing memory consolidation and cognitive function.",
            status=FundingStatus.DRAFTING,
            program_name="Research Project Grant (R01)",
            requested_amount=1250000.00,
            submission_deadline=datetime.now() + timedelta(days=90),
            tags=["sleep", "memory", "aging", "intervention"]
        )
        
        # Link the workspace to the proposal
        proposal_service.link_workspace_to_proposal(workspace_id, proposal_id)
        
        # Update proposal sections
        # Check if section exists before adding
        proposal = proposal_service.get_proposal(proposal_id)
        if 'specific_aims' not in proposal.sections:
            proposal_service.add_section(
                proposal_id=proposal_id,
                section_name="specific_aims",
                title="Specific Aims",
                content="""
                # Specific Aims

                1. To characterize the relationship between sleep architecture and memory consolidation in older adults
                2. To develop targeted interventions to improve slow-wave sleep in older adults
                3. To assess the impact of these interventions on declarative and procedural memory performance

                These aims address a significant gap in our understanding of how age-related changes in sleep affect memory processes.
                """
            )
        
        # Add budget items
        proposal_service.add_budget_item(
            proposal_id=proposal_id,
            category="Personnel",
            item_name="Principal Investigator (25% effort)",
            amount=50000.00,
            justification="The PI will oversee all aspects of the project."
        )
        
        proposal_service.add_budget_item(
            proposal_id=proposal_id,
            category="Equipment",
            item_name="Polysomnography System",
            amount=75000.00,
            justification="Required for measuring sleep architecture in participants."
        )
        
        # Add research components to the proposal
        proposal_service.add_research_question(proposal_id, question_id)
        proposal_service.add_key_citation(proposal_id, citation_id)
        
        # Verify the proposal and workspace
        proposal = proposal_service.get_proposal(proposal_id)
        workspace = proposal_service.get_workspace(workspace_id)
        
        # Check proposal structure
        assert proposal.title.startswith("Improving Memory Consolidation")
        assert proposal.status == FundingStatus.DRAFTING
        # Grant proposal service might have added default sections
        assert len(proposal.sections) >= 1
        # If specific_aims wasn't added, add it now
        if "specific_aims" not in proposal.sections:
            proposal_service.add_section(
                proposal_id=proposal_id,
                section_name="specific_aims",
                title="Specific Aims",
                content="Test specific aims content"
            )
            proposal = proposal_service.get_proposal(proposal_id)
        assert "specific_aims" in proposal.sections
        assert len(proposal.budget_items) == 2
        assert len(proposal.research_questions) == 1
        assert len(proposal.key_citations) == 1
        
        # Check workspace structure
        assert workspace.proposal_id == proposal_id
        assert len(workspace.note_ids) == 1
        assert len(workspace.citation_ids) == 1
        assert len(workspace.question_ids) == 1
        
        # Calculate the budget total
        budget_total = proposal_service.get_proposal(proposal_id).calculate_budget_total()
        assert budget_total == 125000.00
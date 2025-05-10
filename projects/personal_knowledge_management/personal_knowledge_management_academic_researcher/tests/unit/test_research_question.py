"""
Unit tests for the research question framework functionality.
"""

import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from academic_knowledge_vault.models.base import KnowledgeItemType, Reference
from academic_knowledge_vault.models.research_question import (
    Evidence,
    EvidenceStrength,
    EvidenceType,
    Hypothesis,
    HypothesisStatus,
    ResearchQuestion,
    ResearchQuestionStatus,
    ResearchQuestionCollection
)
from academic_knowledge_vault.storage.research_question_storage import (
    EvidenceStorage,
    HypothesisStorage,
    ResearchQuestionStorage,
    ResearchQuestionCollectionStorage
)
from academic_knowledge_vault.services.research_question.research_question_service import ResearchQuestionService


class TestEvidenceStorage:
    """Tests for the EvidenceStorage class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def evidence_storage(self, storage_dir):
        """Create an EvidenceStorage instance."""
        return EvidenceStorage(storage_dir)
    
    def test_save_and_get_evidence(self, evidence_storage):
        """Test saving and retrieving evidence."""
        # Create test evidence
        evidence = Evidence(
            title="Experimental Evidence",
            description="Evidence from experiment X",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.STRONG,
            confidence_score=0.8,
            tags={"experiment", "supporting"}
        )
        
        # Save the evidence
        evidence_id = evidence_storage.save(evidence)
        
        # Retrieve the evidence
        retrieved_evidence = evidence_storage.get(evidence_id)
        
        # Verify the evidence
        assert retrieved_evidence.id == evidence_id
        assert retrieved_evidence.title == "Experimental Evidence"
        assert retrieved_evidence.description == "Evidence from experiment X"
        assert retrieved_evidence.evidence_type == EvidenceType.SUPPORTING
        assert retrieved_evidence.strength == EvidenceStrength.STRONG
        assert retrieved_evidence.confidence_score == 0.8
        assert retrieved_evidence.tags == {"experiment", "supporting"}
    
    def test_get_by_strength(self, evidence_storage):
        """Test getting evidence by strength."""
        # Create test evidence with different strengths
        evidence1 = Evidence(
            title="Strong Evidence",
            description="Strong evidence",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.STRONG
        )
        evidence2 = Evidence(
            title="Moderate Evidence",
            description="Moderate evidence",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.MODERATE
        )
        evidence3 = Evidence(
            title="Weak Evidence",
            description="Weak evidence",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.WEAK
        )
        
        # Save the evidence
        evidence_id1 = evidence_storage.save(evidence1)
        evidence_id2 = evidence_storage.save(evidence2)
        evidence_id3 = evidence_storage.save(evidence3)
        
        # Get evidence by strength
        results = evidence_storage.get_by_strength(EvidenceStrength.STRONG)
        assert len(results) == 1
        assert evidence_id1 in results
        
        results = evidence_storage.get_by_strength(EvidenceStrength.MODERATE)
        assert len(results) == 1
        assert evidence_id2 in results
    
    def test_get_by_type(self, evidence_storage):
        """Test getting evidence by type."""
        # Create test evidence with different types
        evidence1 = Evidence(
            title="Supporting Evidence",
            description="Supporting evidence",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.MODERATE
        )
        evidence2 = Evidence(
            title="Contradicting Evidence",
            description="Contradicting evidence",
            evidence_type=EvidenceType.CONTRADICTING,
            strength=EvidenceStrength.MODERATE
        )
        evidence3 = Evidence(
            title="Methodological Evidence",
            description="Methodological evidence",
            evidence_type=EvidenceType.METHODOLOGY,
            strength=EvidenceStrength.MODERATE
        )
        
        # Save the evidence
        evidence_id1 = evidence_storage.save(evidence1)
        evidence_id2 = evidence_storage.save(evidence2)
        evidence_id3 = evidence_storage.save(evidence3)
        
        # Get evidence by type
        results = evidence_storage.get_by_type(EvidenceType.SUPPORTING)
        assert len(results) == 1
        assert evidence_id1 in results
        
        results = evidence_storage.get_by_type(EvidenceType.CONTRADICTING)
        assert len(results) == 1
        assert evidence_id2 in results
    
    def test_get_supporting(self, evidence_storage):
        """Test getting evidence supporting a specific item."""
        # Create test evidence supporting different items
        evidence1 = Evidence(
            title="Supporting H1",
            description="Evidence supporting H1",
            evidence_type=EvidenceType.SUPPORTING,
            supports=[Reference(item_id="h1", item_type=KnowledgeItemType.HYPOTHESIS)]
        )
        evidence2 = Evidence(
            title="Supporting H2",
            description="Evidence supporting H2",
            evidence_type=EvidenceType.SUPPORTING,
            supports=[Reference(item_id="h2", item_type=KnowledgeItemType.HYPOTHESIS)]
        )
        evidence3 = Evidence(
            title="Supporting Both",
            description="Evidence supporting both",
            evidence_type=EvidenceType.SUPPORTING,
            supports=[
                Reference(item_id="h1", item_type=KnowledgeItemType.HYPOTHESIS),
                Reference(item_id="h2", item_type=KnowledgeItemType.HYPOTHESIS)
            ]
        )
        
        # Save the evidence
        evidence_id1 = evidence_storage.save(evidence1)
        evidence_id2 = evidence_storage.save(evidence2)
        evidence_id3 = evidence_storage.save(evidence3)
        
        # Get evidence supporting a specific item
        results = evidence_storage.get_supporting("h1")
        assert len(results) == 2
        assert evidence_id1 in results
        assert evidence_id3 in results
        
        results = evidence_storage.get_supporting("h2")
        assert len(results) == 2
        assert evidence_id2 in results
        assert evidence_id3 in results


class TestHypothesisStorage:
    """Tests for the HypothesisStorage class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def hypothesis_storage(self, storage_dir):
        """Create a HypothesisStorage instance."""
        return HypothesisStorage(storage_dir)
    
    def test_save_and_get_hypothesis(self, hypothesis_storage):
        """Test saving and retrieving a hypothesis."""
        # Create a test hypothesis
        hypothesis = Hypothesis(
            title="Test Hypothesis",
            statement="This is a test hypothesis statement.",
            status=HypothesisStatus.PROPOSED,
            research_question_id="q123",
            confidence_level=0.7,
            tags={"test", "hypothesis"}
        )
        
        # Save the hypothesis
        hypothesis_id = hypothesis_storage.save(hypothesis)
        
        # Retrieve the hypothesis
        retrieved_hypothesis = hypothesis_storage.get(hypothesis_id)
        
        # Verify the hypothesis
        assert retrieved_hypothesis.id == hypothesis_id
        assert retrieved_hypothesis.title == "Test Hypothesis"
        assert retrieved_hypothesis.statement == "This is a test hypothesis statement."
        assert retrieved_hypothesis.status == HypothesisStatus.PROPOSED
        assert retrieved_hypothesis.research_question_id == "q123"
        assert retrieved_hypothesis.confidence_level == 0.7
        assert retrieved_hypothesis.tags == {"test", "hypothesis"}
    
    def test_get_by_status(self, hypothesis_storage):
        """Test getting hypotheses by status."""
        # Create test hypotheses with different statuses
        hypothesis1 = Hypothesis(
            title="Proposed Hypothesis",
            statement="Proposed hypothesis statement",
            status=HypothesisStatus.PROPOSED
        )
        hypothesis2 = Hypothesis(
            title="Investigating Hypothesis",
            statement="Investigating hypothesis statement",
            status=HypothesisStatus.INVESTIGATING
        )
        hypothesis3 = Hypothesis(
            title="Supported Hypothesis",
            statement="Supported hypothesis statement",
            status=HypothesisStatus.SUPPORTED
        )
        
        # Save the hypotheses
        hypothesis_id1 = hypothesis_storage.save(hypothesis1)
        hypothesis_id2 = hypothesis_storage.save(hypothesis2)
        hypothesis_id3 = hypothesis_storage.save(hypothesis3)
        
        # Get hypotheses by status
        results = hypothesis_storage.get_by_status(HypothesisStatus.PROPOSED)
        assert len(results) == 1
        assert hypothesis_id1 in results
        
        results = hypothesis_storage.get_by_status(HypothesisStatus.INVESTIGATING)
        assert len(results) == 1
        assert hypothesis_id2 in results
    
    def test_get_by_research_question(self, hypothesis_storage):
        """Test getting hypotheses for a specific research question."""
        # Create test hypotheses for different research questions
        hypothesis1 = Hypothesis(
            title="Hypothesis for Q1",
            statement="Hypothesis for question 1",
            research_question_id="q1"
        )
        hypothesis2 = Hypothesis(
            title="Another Hypothesis for Q1",
            statement="Another hypothesis for question 1",
            research_question_id="q1"
        )
        hypothesis3 = Hypothesis(
            title="Hypothesis for Q2",
            statement="Hypothesis for question 2",
            research_question_id="q2"
        )
        
        # Save the hypotheses
        hypothesis_id1 = hypothesis_storage.save(hypothesis1)
        hypothesis_id2 = hypothesis_storage.save(hypothesis2)
        hypothesis_id3 = hypothesis_storage.save(hypothesis3)
        
        # Get hypotheses by research question
        results = hypothesis_storage.get_by_research_question("q1")
        assert len(results) == 2
        assert hypothesis_id1 in results
        assert hypothesis_id2 in results
        
        results = hypothesis_storage.get_by_research_question("q2")
        assert len(results) == 1
        assert hypothesis_id3 in results
    
    def test_get_by_confidence(self, hypothesis_storage):
        """Test getting hypotheses within a confidence range."""
        # Create test hypotheses with different confidence levels
        hypothesis1 = Hypothesis(
            title="Low Confidence",
            statement="Low confidence hypothesis",
            confidence_level=0.2
        )
        hypothesis2 = Hypothesis(
            title="Medium Confidence",
            statement="Medium confidence hypothesis",
            confidence_level=0.5
        )
        hypothesis3 = Hypothesis(
            title="High Confidence",
            statement="High confidence hypothesis",
            confidence_level=0.8
        )
        
        # Save the hypotheses
        hypothesis_id1 = hypothesis_storage.save(hypothesis1)
        hypothesis_id2 = hypothesis_storage.save(hypothesis2)
        hypothesis_id3 = hypothesis_storage.save(hypothesis3)
        
        # Get hypotheses by confidence range
        results = hypothesis_storage.get_by_confidence(0.4, 0.9)
        assert len(results) == 2
        assert hypothesis_id2 in results
        assert hypothesis_id3 in results
        
        results = hypothesis_storage.get_by_confidence(0.7, 1.0)
        assert len(results) == 1
        assert hypothesis_id3 in results


class TestResearchQuestionStorage:
    """Tests for the ResearchQuestionStorage class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def question_storage(self, storage_dir):
        """Create a ResearchQuestionStorage instance."""
        return ResearchQuestionStorage(storage_dir)
    
    def test_save_and_get_question(self, question_storage):
        """Test saving and retrieving a research question."""
        # Create a test research question
        question = ResearchQuestion(
            title="Test Question",
            question="What is the effect of X on Y?",
            description="This is a test research question.",
            status=ResearchQuestionStatus.ACTIVE,
            priority=2,
            knowledge_gaps=["Gap 1", "Gap 2"],
            tags={"test", "research"}
        )
        
        # Save the question
        question_id = question_storage.save(question)
        
        # Retrieve the question
        retrieved_question = question_storage.get(question_id)
        
        # Verify the question
        assert retrieved_question.id == question_id
        assert retrieved_question.title == "Test Question"
        assert retrieved_question.question == "What is the effect of X on Y?"
        assert retrieved_question.description == "This is a test research question."
        assert retrieved_question.status == ResearchQuestionStatus.ACTIVE
        assert retrieved_question.priority == 2
        assert retrieved_question.knowledge_gaps == ["Gap 1", "Gap 2"]
        assert retrieved_question.tags == {"test", "research"}
    
    def test_get_by_status(self, question_storage):
        """Test getting research questions by status."""
        # Create test questions with different statuses
        question1 = ResearchQuestion(
            title="Active Question",
            question="Active question?",
            status=ResearchQuestionStatus.ACTIVE
        )
        question2 = ResearchQuestion(
            title="Completed Question",
            question="Completed question?",
            status=ResearchQuestionStatus.COMPLETED
        )
        question3 = ResearchQuestion(
            title="On Hold Question",
            question="On hold question?",
            status=ResearchQuestionStatus.ON_HOLD
        )
        
        # Save the questions
        question_id1 = question_storage.save(question1)
        question_id2 = question_storage.save(question2)
        question_id3 = question_storage.save(question3)
        
        # Get questions by status
        results = question_storage.get_by_status(ResearchQuestionStatus.ACTIVE)
        assert len(results) == 1
        assert question_id1 in results
        
        results = question_storage.get_by_status(ResearchQuestionStatus.COMPLETED)
        assert len(results) == 1
        assert question_id2 in results
    
    def test_get_by_priority(self, question_storage):
        """Test getting research questions by priority."""
        # Create test questions with different priorities
        question1 = ResearchQuestion(
            title="High Priority",
            question="High priority question?",
            priority=1
        )
        question2 = ResearchQuestion(
            title="Medium Priority",
            question="Medium priority question?",
            priority=3
        )
        question3 = ResearchQuestion(
            title="Low Priority",
            question="Low priority question?",
            priority=5
        )
        
        # Save the questions
        question_id1 = question_storage.save(question1)
        question_id2 = question_storage.save(question2)
        question_id3 = question_storage.save(question3)
        
        # Get questions by priority
        results = question_storage.get_by_priority(1)
        assert len(results) == 1
        assert question_id1 in results
        
        results = question_storage.get_by_priority(3)
        assert len(results) == 1
        assert question_id2 in results
    
    def test_get_with_knowledge_gaps(self, question_storage):
        """Test getting research questions with knowledge gaps."""
        # Create test questions with and without knowledge gaps
        question1 = ResearchQuestion(
            title="Question with Gaps",
            question="Question with gaps?",
            knowledge_gaps=["Gap 1", "Gap 2"]
        )
        question2 = ResearchQuestion(
            title="Another Question with Gaps",
            question="Another question with gaps?",
            knowledge_gaps=["Gap 3"]
        )
        question3 = ResearchQuestion(
            title="Question without Gaps",
            question="Question without gaps?"
        )
        
        # Save the questions
        question_id1 = question_storage.save(question1)
        question_id2 = question_storage.save(question2)
        question_id3 = question_storage.save(question3)
        
        # Get questions with knowledge gaps
        results = question_storage.get_with_knowledge_gaps()
        assert len(results) == 2
        assert question_id1 in results
        assert question_id2 in results
        assert question_id3 not in results


class TestResearchQuestionService:
    """Tests for the ResearchQuestionService class."""
    
    @pytest.fixture
    def storage_dir(self):
        """Create a temporary directory for storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def question_service(self, storage_dir):
        """Create a ResearchQuestionService instance."""
        question_storage = ResearchQuestionStorage(Path(storage_dir) / "questions")
        hypothesis_storage = HypothesisStorage(Path(storage_dir) / "hypotheses")
        evidence_storage = EvidenceStorage(Path(storage_dir) / "evidence")
        collection_storage = ResearchQuestionCollectionStorage(Path(storage_dir) / "collections")
        return ResearchQuestionService(
            question_storage, hypothesis_storage, evidence_storage, collection_storage
        )
    
    def test_create_research_question(self, question_service):
        """Test creating a research question."""
        # Create a research question
        question_id = question_service.create_research_question(
            question="What is the impact of X on Y?",
            description="Investigating the relationship between X and Y",
            tags=["x", "y", "impact"],
            priority=2,
            status=ResearchQuestionStatus.ACTIVE,
            knowledge_gaps=["Gap in understanding mechanism", "Gap in long-term effects"]
        )
        
        # Retrieve the question
        question = question_service.get_research_question(question_id)
        
        # Verify the question
        assert question.question == "What is the impact of X on Y?"
        assert question.description == "Investigating the relationship between X and Y"
        assert question.tags == {"x", "y", "impact"}
        assert question.priority == 2
        assert question.status == ResearchQuestionStatus.ACTIVE
        assert "Gap in understanding mechanism" in question.knowledge_gaps
        assert "Gap in long-term effects" in question.knowledge_gaps
    
    def test_update_research_question(self, question_service):
        """Test updating a research question."""
        # Create a research question
        question_id = question_service.create_research_question(
            question="Original question?",
            description="Original description",
            tags=["original"],
            priority=3
        )
        
        # Update the question
        question_service.update_research_question(
            question_id=question_id,
            question="Updated question?",
            description="Updated description",
            tags=["updated"],
            priority=1,
            status=ResearchQuestionStatus.COMPLETED
        )
        
        # Retrieve the updated question
        question = question_service.get_research_question(question_id)
        
        # Verify the updates
        assert question.question == "Updated question?"
        assert question.description == "Updated description"
        assert question.tags == {"updated"}
        assert question.priority == 1
        assert question.status == ResearchQuestionStatus.COMPLETED
    
    def test_add_knowledge_gap(self, question_service):
        """Test adding a knowledge gap to a research question."""
        # Create a research question
        question_id = question_service.create_research_question(
            question="Research question?"
        )
        
        # Add a knowledge gap
        question_service.add_knowledge_gap(
            question_id=question_id,
            gap_description="Important knowledge gap"
        )
        
        # Retrieve the question
        question = question_service.get_research_question(question_id)
        
        # Verify the knowledge gap was added
        assert "Important knowledge gap" in question.knowledge_gaps
    
    def test_create_hypothesis(self, question_service):
        """Test creating a hypothesis."""
        # Create a research question
        question_id = question_service.create_research_question(
            question="What is the effect of X on Y?"
        )
        
        # Create a hypothesis for the question
        hypothesis_id = question_service.create_hypothesis(
            statement="X increases Y through mechanism Z",
            research_question_id=question_id,
            status=HypothesisStatus.PROPOSED,
            tags=["mechanism", "increase"],
            confidence_level=0.5
        )
        
        # Retrieve the hypothesis
        hypothesis = question_service.get_hypothesis(hypothesis_id)
        
        # Verify the hypothesis
        assert hypothesis.statement == "X increases Y through mechanism Z"
        assert hypothesis.research_question_id == question_id
        assert hypothesis.status == HypothesisStatus.PROPOSED
        assert hypothesis.tags == {"mechanism", "increase"}
        assert hypothesis.confidence_level == 0.5
        
        # Verify the hypothesis was added to the research question
        question = question_service.get_research_question(question_id)
        hypothesis_found = False
        for ref in question.hypotheses:
            if ref.item_id == hypothesis_id:
                hypothesis_found = True
                break
        assert hypothesis_found
    
    def test_update_hypothesis(self, question_service):
        """Test updating a hypothesis."""
        # Create a research question and hypothesis
        question_id = question_service.create_research_question(
            question="Research question?"
        )
        hypothesis_id = question_service.create_hypothesis(
            statement="Original hypothesis",
            research_question_id=question_id,
            status=HypothesisStatus.PROPOSED,
            confidence_level=0.3
        )
        
        # Update the hypothesis
        question_service.update_hypothesis(
            hypothesis_id=hypothesis_id,
            statement="Updated hypothesis",
            status=HypothesisStatus.SUPPORTED,
            confidence_level=0.7
        )
        
        # Retrieve the updated hypothesis
        hypothesis = question_service.get_hypothesis(hypothesis_id)
        
        # Verify the updates
        assert hypothesis.statement == "Updated hypothesis"
        assert hypothesis.status == HypothesisStatus.SUPPORTED
        assert hypothesis.confidence_level == 0.7
    
    def test_create_evidence(self, question_service):
        """Test creating evidence."""
        # Create a research question and hypothesis
        question_id = question_service.create_research_question(
            question="Research question?"
        )
        hypothesis_id = question_service.create_hypothesis(
            statement="Hypothesis",
            research_question_id=question_id
        )
        
        # Create supporting evidence
        evidence_id = question_service.create_evidence(
            description="Experimental results supporting the hypothesis",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.STRONG,
            source_id="experiment123",
            source_type=KnowledgeItemType.EXPERIMENT,
            supports_ids=[hypothesis_id],
            confidence_score=0.9,
            methodology_notes="Rigorous methodology",
            tags=["experiment", "supporting"]
        )
        
        # Retrieve the evidence
        evidence = question_service.get_evidence(evidence_id)
        
        # Verify the evidence
        assert evidence.description == "Experimental results supporting the hypothesis"
        assert evidence.evidence_type == EvidenceType.SUPPORTING
        assert evidence.strength == EvidenceStrength.STRONG
        assert evidence.source.item_id == "experiment123"
        assert evidence.source.item_type == KnowledgeItemType.EXPERIMENT
        assert evidence.confidence_score == 0.9
        assert evidence.methodology_notes == "Rigorous methodology"
        assert evidence.tags == {"experiment", "supporting"}
        
        # Verify there's a reference to the hypothesis
        assert len(evidence.supports) == 1
        assert evidence.supports[0].item_id == hypothesis_id
        
        # Verify the hypothesis has a reference to the evidence
        hypothesis = question_service.get_hypothesis(hypothesis_id)
        evidence_found = False
        for ref in hypothesis.supporting_evidence:
            if ref.item_id == evidence_id:
                evidence_found = True
                break
        assert evidence_found
    
    def test_calculate_evidence_strength(self, question_service):
        """Test calculating evidence strength for a hypothesis."""
        # Create a research question and hypothesis
        question_id = question_service.create_research_question(
            question="Research question?"
        )
        hypothesis_id = question_service.create_hypothesis(
            statement="Hypothesis",
            research_question_id=question_id
        )
        
        # Create supporting evidence
        supporting_id1 = question_service.create_evidence(
            description="Strong supporting evidence",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.STRONG,
            supports_ids=[hypothesis_id],
            confidence_score=0.9
        )
        supporting_id2 = question_service.create_evidence(
            description="Moderate supporting evidence",
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.MODERATE,
            supports_ids=[hypothesis_id],
            confidence_score=0.7
        )
        
        # Create contradicting evidence
        contradicting_id = question_service.create_evidence(
            description="Contradicting evidence",
            evidence_type=EvidenceType.CONTRADICTING,
            strength=EvidenceStrength.MODERATE,
            contradicts_ids=[hypothesis_id],
            confidence_score=0.6
        )
        
        # Calculate evidence strength
        strength_score = question_service.calculate_evidence_strength(hypothesis_id)
        
        # Verify the strength score (exact value depends on the calculation implementation)
        assert 0 <= strength_score <= 1
        
        # The score should be greater than 0.5 since there is more supporting than contradicting evidence
        assert strength_score > 0.5
        
        # Verify the score was saved to the hypothesis
        hypothesis = question_service.get_hypothesis(hypothesis_id)
        assert hypothesis.evidence_strength_score == strength_score
    
    def test_search_questions(self, question_service):
        """Test searching for research questions based on various criteria."""
        # Create test research questions
        question_id1 = question_service.create_research_question(
            question="What is the effect of treatment X on condition Y?",
            status=ResearchQuestionStatus.ACTIVE,
            priority=1,
            tags=["treatment", "condition"],
            knowledge_gaps=["Mechanism unknown"]
        )
        question_id2 = question_service.create_research_question(
            question="How does factor A influence process B?",
            status=ResearchQuestionStatus.ACTIVE,
            priority=2,
            tags=["factor", "process"]
        )
        question_id3 = question_service.create_research_question(
            question="What is the long-term effect of intervention C?",
            status=ResearchQuestionStatus.COMPLETED,
            priority=3,
            tags=["intervention", "long-term"]
        )
        
        # Search by text
        results = question_service.search_questions(text="effect")
        assert len(results) == 2
        assert question_id1 in results
        assert question_id3 in results
        
        # Search by tags
        results = question_service.search_questions(tags=["treatment"])
        assert len(results) == 1
        assert question_id1 in results
        
        # Search by status
        results = question_service.search_questions(status=ResearchQuestionStatus.ACTIVE)
        assert len(results) == 2
        assert question_id1 in results
        assert question_id2 in results
        
        # Search by priority
        results = question_service.search_questions(priority=1)
        assert len(results) == 1
        assert question_id1 in results
        
        # Search by knowledge gaps
        results = question_service.search_questions(has_knowledge_gaps=True)
        assert len(results) == 1
        assert question_id1 in results
        
        # Search with multiple criteria
        results = question_service.search_questions(
            text="effect",
            status=ResearchQuestionStatus.ACTIVE
        )
        assert len(results) == 1
        assert question_id1 in results
    
    def test_search_hypotheses(self, question_service):
        """Test searching for hypotheses based on various criteria."""
        # Create a research question
        question_id = question_service.create_research_question(
            question="Main research question?"
        )
        
        # Create test hypotheses
        hypothesis_id1 = question_service.create_hypothesis(
            statement="Treatment X reduces symptoms through mechanism Y",
            research_question_id=question_id,
            status=HypothesisStatus.PROPOSED,
            tags=["treatment", "mechanism"],
            confidence_level=0.3
        )
        hypothesis_id2 = question_service.create_hypothesis(
            statement="Factor A increases process B via pathway C",
            research_question_id=question_id,
            status=HypothesisStatus.INVESTIGATING,
            tags=["factor", "pathway"],
            confidence_level=0.5
        )
        hypothesis_id3 = question_service.create_hypothesis(
            statement="Intervention leads to long-term benefits",
            status=HypothesisStatus.SUPPORTED,
            tags=["intervention", "long-term"],
            confidence_level=0.8
        )
        
        # Search by text
        results = question_service.search_hypotheses(text="mechanism")
        assert len(results) == 1
        assert hypothesis_id1 in results
        
        # Search by tags
        results = question_service.search_hypotheses(tags=["long-term"])
        assert len(results) == 1
        assert hypothesis_id3 in results
        
        # Search by status
        results = question_service.search_hypotheses(status=HypothesisStatus.PROPOSED)
        assert len(results) == 1
        assert hypothesis_id1 in results
        
        # Search by research question
        results = question_service.search_hypotheses(research_question_id=question_id)
        assert len(results) == 2
        assert hypothesis_id1 in results
        assert hypothesis_id2 in results
        
        # Search by confidence range
        results = question_service.search_hypotheses(min_confidence=0.7, max_confidence=1.0)
        assert len(results) == 1
        assert hypothesis_id3 in results
        
        # Search with multiple criteria
        results = question_service.search_hypotheses(
            text="factor",
            research_question_id=question_id
        )
        assert len(results) == 1
        assert hypothesis_id2 in results
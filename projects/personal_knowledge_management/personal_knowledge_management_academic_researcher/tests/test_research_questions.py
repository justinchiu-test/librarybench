"""Tests for research question and evidence relationship mapping."""

import tempfile
import shutil
from uuid import UUID, uuid4

import pytest
import networkx as nx

from researchbrain.core.brain import ResearchBrain
from researchbrain.core.models import (
    Citation, EvidenceStrength, EvidenceType, Evidence, Note, ResearchQuestion
)


class TestResearchQuestions:
    """Tests for research question and evidence relationship mapping."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Fixture that creates a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def brain(self, temp_data_dir):
        """Fixture that creates a ResearchBrain instance."""
        return ResearchBrain(temp_data_dir)
    
    def test_create_research_question(self, brain):
        """Test creating a research question with all attributes."""
        # Create a research question with all fields
        question_id = brain.create_research_question(
            question="What are the neural mechanisms of autobiographical memory?",
            description="Investigating the brain regions and processes involved in personal memory.",
            tags={"memory", "neuroscience", "autobiographical"},
            status="open",
            priority=8
        )
        
        # Retrieve the question
        question = brain.storage.get(ResearchQuestion, question_id)
        
        # Verify all attributes
        assert question is not None
        assert question.id == question_id
        assert question.question == "What are the neural mechanisms of autobiographical memory?"
        assert question.description == "Investigating the brain regions and processes involved in personal memory."
        assert question.tags == {"memory", "neuroscience", "autobiographical"}
        assert question.status == "open"
        assert question.priority == 8
        assert question.evidence == []
        
        # Verify in knowledge graph
        assert brain._knowledge_graph.has_node(str(question_id))
        node_data = brain._knowledge_graph.nodes[str(question_id)]
        assert node_data["type"] == "question"
        assert node_data["title"] == "What are the neural mechanisms of autobiographical memory?"
    
    def test_adding_supporting_evidence(self, brain):
        """Test adding supporting evidence to a research question."""
        # Create a research question
        question_id = brain.create_research_question(
            question="Does caffeine improve cognitive performance?",
            priority=7
        )
        
        # Create a note with supporting evidence
        note_id = brain.create_note(
            title="Caffeine Study Results",
            content="Multiple studies show improved reaction time after caffeine consumption."
        )
        
        # Create a citation for the evidence
        citation_id = brain.create_citation(
            title="Effects of Caffeine on Cognitive Performance",
            authors=["Smith, J.", "Johnson, K."],
            year=2021,
            journal="Journal of Cognitive Enhancement"
        )
        
        # Link the note to the citation
        brain.link_note_to_paper(note_id, citation_id)
        
        # Add supporting evidence to the question
        evidence_id = brain.add_evidence_to_question(
            question_id=question_id,
            note_id=note_id,
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.STRONG,
            description="Clear improvement in reaction time tests",
            citation_ids=[citation_id]
        )
        
        # Verify evidence was added correctly
        question = brain.storage.get(ResearchQuestion, question_id)
        
        assert len(question.evidence) == 1
        evidence = question.evidence[0]
        
        assert evidence.id == evidence_id
        assert evidence.note_id == note_id
        assert evidence.evidence_type == EvidenceType.SUPPORTING
        assert evidence.strength == EvidenceStrength.STRONG
        assert evidence.description == "Clear improvement in reaction time tests"
        assert len(evidence.citation_ids) == 1
        assert evidence.citation_ids[0] == citation_id
        
        # Verify knowledge graph connection
        assert brain._knowledge_graph.has_edge(str(question_id), str(note_id))
        edge_data = brain._knowledge_graph.get_edge_data(str(question_id), str(note_id))
        assert edge_data["type"] == "evidence"
        assert edge_data["evidence_type"] == EvidenceType.SUPPORTING
        assert edge_data["strength"] == EvidenceStrength.STRONG
    
    def test_adding_contradicting_evidence(self, brain):
        """Test adding contradicting evidence to a research question."""
        # Create a research question
        question_id = brain.create_research_question(
            question="Is meditation effective for reducing anxiety?",
            priority=9
        )
        
        # Create a note with contradicting evidence
        note_id = brain.create_note(
            title="Critical Review of Meditation Studies",
            content="Meta-analysis found no significant effect in placebo-controlled trials."
        )
        
        # Add contradicting evidence to the question
        evidence_id = brain.add_evidence_to_question(
            question_id=question_id,
            note_id=note_id,
            evidence_type=EvidenceType.CONTRADICTING,
            strength=EvidenceStrength.MODERATE,
            description="Meta-analysis challenges efficacy claims"
        )
        
        # Verify evidence was added correctly
        question = brain.storage.get(ResearchQuestion, question_id)
        
        assert len(question.evidence) == 1
        evidence = question.evidence[0]
        
        assert evidence.id == evidence_id
        assert evidence.note_id == note_id
        assert evidence.evidence_type == EvidenceType.CONTRADICTING
        assert evidence.strength == EvidenceStrength.MODERATE
        assert evidence.description == "Meta-analysis challenges efficacy claims"
        
        # Verify knowledge graph connection
        assert brain._knowledge_graph.has_edge(str(question_id), str(note_id))
        edge_data = brain._knowledge_graph.get_edge_data(str(question_id), str(note_id))
        assert edge_data["type"] == "evidence"
        assert edge_data["evidence_type"] == EvidenceType.CONTRADICTING
        assert edge_data["strength"] == EvidenceStrength.MODERATE
    
    def test_balanced_evidence_evaluation(self, brain):
        """Test evaluating both supporting and contradicting evidence for a question."""
        # Create a research question
        question_id = brain.create_research_question(
            question="Do omega-3 supplements improve cardiovascular health?",
            description="Examining the effects of omega-3 fatty acid supplementation on heart health metrics.",
            priority=8
        )
        
        # Create supporting evidence
        supporting_note_id = brain.create_note(
            title="Positive Omega-3 Study",
            content="Clinical trial showing reduced triglyceride levels with omega-3 supplementation."
        )
        
        supporting_citation_id = brain.create_citation(
            title="Omega-3 Fatty Acids and Cardiovascular Disease: Effects on Risk Factors, Molecular Pathways, and Clinical Events",
            authors=["Harris, W. S.", "Miller, M."],
            year=2019,
            journal="Journal of the American Heart Association"
        )
        
        brain.link_note_to_paper(supporting_note_id, supporting_citation_id)
        
        # Create contradicting evidence
        contradicting_note_id = brain.create_note(
            title="Negative Omega-3 Study",
            content="Large-scale trial found no significant effect on major cardiovascular events."
        )
        
        contradicting_citation_id = brain.create_citation(
            title="Marine n-3 Fatty Acids and Prevention of Cardiovascular Disease and Cancer",
            authors=["Manson, J. E.", "Cook, N. R."],
            year=2020,
            journal="New England Journal of Medicine"
        )
        
        brain.link_note_to_paper(contradicting_note_id, contradicting_citation_id)
        
        # Create inconclusive evidence
        inconclusive_note_id = brain.create_note(
            title="Mixed Results Study",
            content="Inconsistent effects across different cardiovascular markers."
        )
        
        # Add all evidence types to the question
        brain.add_evidence_to_question(
            question_id=question_id,
            note_id=supporting_note_id,
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.STRONG,
            description="Clinical trial with significant reduction in triglycerides",
            citation_ids=[supporting_citation_id]
        )
        
        brain.add_evidence_to_question(
            question_id=question_id,
            note_id=contradicting_note_id,
            evidence_type=EvidenceType.CONTRADICTING,
            strength=EvidenceStrength.STRONG,
            description="No effect on major cardiovascular events in large trial",
            citation_ids=[contradicting_citation_id]
        )
        
        brain.add_evidence_to_question(
            question_id=question_id,
            note_id=inconclusive_note_id,
            evidence_type=EvidenceType.INCONCLUSIVE,
            strength=EvidenceStrength.MODERATE,
            description="Mixed results across different markers"
        )
        
        # Verify all evidence was added
        question = brain.storage.get(ResearchQuestion, question_id)
        
        assert len(question.evidence) == 3
        
        # Count by evidence type
        evidence_types = [e.evidence_type for e in question.evidence]
        assert evidence_types.count(EvidenceType.SUPPORTING) == 1
        assert evidence_types.count(EvidenceType.CONTRADICTING) == 1
        assert evidence_types.count(EvidenceType.INCONCLUSIVE) == 1
        
        # Verify the strength assignments
        for evidence in question.evidence:
            if evidence.evidence_type == EvidenceType.INCONCLUSIVE:
                assert evidence.strength == EvidenceStrength.MODERATE
            else:
                assert evidence.strength == EvidenceStrength.STRONG
        
        # Verify all connections in the knowledge graph
        assert brain._knowledge_graph.has_edge(str(question_id), str(supporting_note_id))
        assert brain._knowledge_graph.has_edge(str(question_id), str(contradicting_note_id))
        assert brain._knowledge_graph.has_edge(str(question_id), str(inconclusive_note_id))
    
    def test_evidence_strength_levels(self, brain):
        """Test different evidence strength levels."""
        # Create a research question
        question_id = brain.create_research_question(
            question="How effective are mindfulness interventions for depression?",
            priority=7
        )
        
        # Create notes for different strength levels
        strong_note_id = brain.create_note(
            title="Strong Evidence",
            content="Multiple randomized controlled trials show significant effect."
        )
        
        moderate_note_id = brain.create_note(
            title="Moderate Evidence",
            content="Several studies show effects but with methodological limitations."
        )
        
        weak_note_id = brain.create_note(
            title="Weak Evidence",
            content="Limited observational studies with potential confounds."
        )
        
        anecdotal_note_id = brain.create_note(
            title="Anecdotal Evidence",
            content="Case reports and testimonials without controlled conditions."
        )
        
        # Add evidence with different strength levels
        brain.add_evidence_to_question(
            question_id=question_id,
            note_id=strong_note_id,
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.STRONG,
            description="Multiple high-quality RCTs"
        )
        
        brain.add_evidence_to_question(
            question_id=question_id,
            note_id=moderate_note_id,
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.MODERATE,
            description="Several studies with limitations"
        )
        
        brain.add_evidence_to_question(
            question_id=question_id,
            note_id=weak_note_id,
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.WEAK,
            description="Limited observational data"
        )
        
        brain.add_evidence_to_question(
            question_id=question_id,
            note_id=anecdotal_note_id,
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.ANECDOTAL,
            description="Uncontrolled case reports"
        )
        
        # Verify all strength levels were recorded correctly
        question = brain.storage.get(ResearchQuestion, question_id)
        
        assert len(question.evidence) == 4
        
        # Check that each strength level exists
        strengths = [e.strength for e in question.evidence]
        assert EvidenceStrength.STRONG in strengths
        assert EvidenceStrength.MODERATE in strengths
        assert EvidenceStrength.WEAK in strengths
        assert EvidenceStrength.ANECDOTAL in strengths
        
        # Verify corresponding knowledge graph edge attributes
        for note_id, strength in [
            (strong_note_id, EvidenceStrength.STRONG),
            (moderate_note_id, EvidenceStrength.MODERATE),
            (weak_note_id, EvidenceStrength.WEAK),
            (anecdotal_note_id, EvidenceStrength.ANECDOTAL)
        ]:
            edge_data = brain._knowledge_graph.get_edge_data(str(question_id), str(note_id))
            assert edge_data["strength"] == strength
    
    def test_evidence_with_multiple_citations(self, brain):
        """Test evidence supported by multiple citations."""
        # Create a research question
        question_id = brain.create_research_question(
            question="What dietary factors influence gut microbiome composition?",
            priority=8
        )
        
        # Create a note summarizing multiple studies
        note_id = brain.create_note(
            title="Dietary Fiber and Microbiome",
            content="Multiple studies show that dietary fiber increases beneficial bacteria."
        )
        
        # Create multiple citations
        citation_ids = []
        for i in range(3):
            citation_id = brain.create_citation(
                title=f"Dietary Fiber Study {i+1}",
                authors=[f"Author {i+1}"],
                year=2020 + i,
                journal="Microbiome Research"
            )
            citation_ids.append(citation_id)
            
            # Link note to each citation
            brain.link_note_to_paper(note_id, citation_id)
        
        # Add evidence with multiple citations
        evidence_id = brain.add_evidence_to_question(
            question_id=question_id,
            note_id=note_id,
            evidence_type=EvidenceType.SUPPORTING,
            strength=EvidenceStrength.STRONG,
            description="Multiple studies on dietary fiber effects",
            citation_ids=citation_ids
        )
        
        # Verify evidence has all citations
        question = brain.storage.get(ResearchQuestion, question_id)
        
        assert len(question.evidence) == 1
        evidence = question.evidence[0]
        
        assert len(evidence.citation_ids) == 3
        for citation_id in citation_ids:
            assert citation_id in evidence.citation_ids
    
    def test_related_questions(self, brain):
        """Test connecting related research questions."""
        # Create multiple related research questions
        main_question_id = brain.create_research_question(
            question="What are the neural correlates of consciousness?",
            priority=9
        )
        
        sub_question1_id = brain.create_research_question(
            question="How does anesthesia affect consciousness?",
            priority=8
        )
        
        sub_question2_id = brain.create_research_question(
            question="What distinguishes conscious from unconscious processing?",
            priority=8
        )
        
        # Create notes that bridge these questions
        bridge_note1_id = brain.create_note(
            title="Consciousness and Anesthesia",
            content="Examining how anesthesia disrupts neural correlates of consciousness."
        )
        
        bridge_note2_id = brain.create_note(
            title="Conscious vs. Unconscious Processing",
            content="Review of differences between conscious and unconscious neural processing."
        )
        
        # Add the bridge notes as evidence for multiple questions
        brain.add_evidence_to_question(
            question_id=main_question_id,
            note_id=bridge_note1_id,
            evidence_type=EvidenceType.RELATED,
            strength=EvidenceStrength.MODERATE,
            description="Connection to anesthesia research"
        )
        
        brain.add_evidence_to_question(
            question_id=sub_question1_id,
            note_id=bridge_note1_id,
            evidence_type=EvidenceType.RELATED,
            strength=EvidenceStrength.STRONG,
            description="Direct relevance to anesthesia effects"
        )
        
        brain.add_evidence_to_question(
            question_id=main_question_id,
            note_id=bridge_note2_id,
            evidence_type=EvidenceType.RELATED,
            strength=EvidenceStrength.MODERATE,
            description="Connection to unconscious processing"
        )
        
        brain.add_evidence_to_question(
            question_id=sub_question2_id,
            note_id=bridge_note2_id,
            evidence_type=EvidenceType.RELATED,
            strength=EvidenceStrength.STRONG,
            description="Direct relevance to consciousness distinctions"
        )
        
        # Verify the connections in the knowledge graph
        # Check if we can navigate between related questions through shared notes
        
        # Get notes connected to the main question
        main_related = brain.get_related_nodes(main_question_id)
        assert "evidence" in main_related
        main_evidence_notes = [n.id for n in main_related["evidence"]]
        
        # Get questions connected to the first bridge note
        bridge1_related = brain.get_related_nodes(bridge_note1_id)
        assert "incoming_evidence" in bridge1_related
        questions_with_bridge1 = [q.id for q in bridge1_related["incoming_evidence"]]
        
        # Verify that both the main question and sub-question 1 are connected to bridge note 1
        assert main_question_id in questions_with_bridge1
        assert sub_question1_id in questions_with_bridge1
        
        # Similarly for bridge note 2
        bridge2_related = brain.get_related_nodes(bridge_note2_id)
        assert "incoming_evidence" in bridge2_related
        questions_with_bridge2 = [q.id for q in bridge2_related["incoming_evidence"]]
        
        assert main_question_id in questions_with_bridge2
        assert sub_question2_id in questions_with_bridge2
"""Fixtures for testing the Scholar's BrainCache knowledge management system."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from typing import Dict, List, Generator, Tuple, Any, Callable


@pytest.fixture
def temp_knowledge_base() -> Generator[Path, None, None]:
    """Provide a temporary directory for knowledge base storage during tests.
    
    Returns:
        Path: Path to the temporary knowledge base directory
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create basic structure for knowledge base
        (temp_dir / "notes").mkdir()
        (temp_dir / "bibliography").mkdir()
        (temp_dir / "templates").mkdir()
        (temp_dir / "workspaces").mkdir()
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_bibtex_entries() -> List[Dict[str, str]]:
    """Provide sample BibTeX entries for testing citation functionality.
    
    Returns:
        List[Dict[str, str]]: List of dictionaries containing BibTeX entry data
    """
    return [
        {
            "id": "smith2020neural",
            "type": "article",
            "title": "Neural mechanisms of cognitive processing",
            "author": "Smith, John and Johnson, Emily",
            "journal": "Journal of Neuroscience",
            "year": "2020",
            "volume": "42",
            "number": "3",
            "pages": "1234-1246",
            "doi": "10.1234/jneurosci.1234-1234.2020"
        },
        {
            "id": "brown2019memory",
            "type": "article",
            "title": "Memory formation in the hippocampus",
            "author": "Brown, Robert and Davis, Sarah",
            "journal": "Neurobiology Reviews",
            "year": "2019",
            "volume": "15",
            "number": "2",
            "pages": "87-104",
            "doi": "10.1234/neurobiol.5678-5678.2019"
        },
        {
            "id": "wilson2021cognitive",
            "type": "book",
            "title": "Cognitive Neuroscience: Principles and Applications",
            "author": "Wilson, Michael",
            "publisher": "Academic Press",
            "year": "2021",
            "isbn": "978-1234567890"
        }
    ]


@pytest.fixture
def sample_research_questions() -> List[Dict[str, Any]]:
    """Provide sample research questions for testing research question tracking.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing research question data
    """
    return [
        {
            "id": "rq-001",
            "question": "How does sleep deprivation affect working memory performance?",
            "hypothesis": "Sleep deprivation will significantly decrease working memory capacity and accuracy.",
            "tags": ["sleep", "working-memory", "cognition"]
        },
        {
            "id": "rq-002",
            "question": "What is the relationship between hippocampal volume and memory retention in older adults?",
            "hypothesis": "Decreased hippocampal volume will correlate with reduced memory retention abilities.",
            "tags": ["hippocampus", "aging", "memory"]
        },
        {
            "id": "rq-003",
            "question": "Can transcranial direct current stimulation enhance cognitive flexibility?",
            "hypothesis": "Anodal tDCS over the prefrontal cortex will improve performance on cognitive flexibility tasks.",
            "tags": ["tDCS", "neuromodulation", "cognitive-flexibility"]
        }
    ]


@pytest.fixture
def sample_notes() -> List[Dict[str, Any]]:
    """Provide sample research notes for testing note management functionality.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing note data
    """
    return [
        {
            "id": "note-001",
            "title": "Sleep deprivation effects on attention",
            "content": """# Sleep deprivation effects on attention
            
According to [[smith2020neural]], even 24 hours of sleep deprivation can lead to significant decreases in sustained attention. This is relevant to [[rq-001]] as working memory heavily relies on attentional resources.

Key findings:
- 30% decrease in vigilance task performance after 24h without sleep
- Error rates increased progressively with time-on-task
- Recovery required 2 full nights of sleep

This contradicts earlier work by Johnson (2015) who found complete recovery after just one night.
            """,
            "tags": ["sleep", "attention", "cognition"],
            "created": "2023-01-15T10:30:00",
            "modified": "2023-01-16T14:45:00"
        },
        {
            "id": "note-002",
            "title": "Hippocampal volumetric changes with age",
            "content": """# Hippocampal volumetric changes with age

[[brown2019memory]] conducted a longitudinal study showing 1.5% annual hippocampal volume decrease in adults over 65.

This is directly relevant to [[rq-002]] regarding hippocampal volume and memory retention.

Recent findings:
- Volume loss is not uniform across hippocampal subfields
- CA1 region shows earliest atrophy
- Dentate gyrus maintains neurogenesis even in older adults

Need to incorporate these anatomical specifics into our hypothesis.
            """,
            "tags": ["hippocampus", "aging", "longitudinal-study"],
            "created": "2023-02-10T09:15:00",
            "modified": "2023-02-10T09:15:00"
        },
        {
            "id": "note-003",
            "title": "tDCS protocols for cognition",
            "content": """# tDCS protocols for cognition

Standard protocols for cognitive enhancement based on [[wilson2021cognitive]]:

- Electrode placement: F3/F4 (DLPFC)
- Current: 1-2 mA
- Duration: 20 minutes
- Montage: anodal over target region

These parameters should be used in our experiments related to [[rq-003]].

Considerations:
- Individual differences in skull thickness affect current flow
- Baseline performance modulates efficacy (ceiling effects)
- Duration of effects typically 1-2 hours post-stimulation
            """,
            "tags": ["tDCS", "methods", "neuromodulation"],
            "created": "2023-03-05T15:45:00",
            "modified": "2023-03-06T11:20:00"
        }
    ]


@pytest.fixture
def sample_experiment_template() -> Dict[str, Any]:
    """Provide a sample experiment template for testing experiment logging functionality.
    
    Returns:
        Dict[str, Any]: Dictionary containing experiment template data
    """
    return {
        "id": "template-behavioral-experiment",
        "name": "Behavioral Experiment Template",
        "fields": [
            {
                "name": "title",
                "type": "string",
                "required": True,
                "description": "Descriptive title of the experiment"
            },
            {
                "name": "research_question",
                "type": "reference",
                "reference_type": "research_question",
                "required": True,
                "description": "The research question this experiment addresses"
            },
            {
                "name": "participants",
                "type": "object",
                "required": True,
                "fields": [
                    {"name": "count", "type": "integer", "required": True},
                    {"name": "age_range", "type": "string", "required": True},
                    {"name": "inclusion_criteria", "type": "string_list", "required": True},
                    {"name": "exclusion_criteria", "type": "string_list", "required": True}
                ]
            },
            {
                "name": "procedure",
                "type": "text",
                "required": True,
                "description": "Detailed experimental procedure"
            },
            {
                "name": "measures",
                "type": "string_list",
                "required": True,
                "description": "Outcome measures collected"
            },
            {
                "name": "equipment",
                "type": "string_list",
                "required": False,
                "description": "Equipment used in the experiment"
            },
            {
                "name": "data_analysis_plan",
                "type": "text",
                "required": True,
                "description": "Planned statistical analyses"
            },
            {
                "name": "notes",
                "type": "text",
                "required": False,
                "description": "Additional notes or observations"
            }
        ]
    }


@pytest.fixture
def sample_grant_workspace() -> Dict[str, Any]:
    """Provide a sample grant workspace configuration for testing grant workspace functionality.
    
    Returns:
        Dict[str, Any]: Dictionary containing grant workspace configuration
    """
    return {
        "id": "grant-nsf-cognitive",
        "name": "NSF Cognitive Neuroscience Grant 2023",
        "description": "Workspace for preparing NSF grant application on cognitive enhancement techniques",
        "deadline": "2023-06-15",
        "sections": [
            {
                "name": "Project Summary",
                "description": "One-page summary of the proposed research",
                "relevant_tags": ["tDCS", "cognition", "enhancement", "summary"]
            },
            {
                "name": "Intellectual Merit",
                "description": "How the project advances knowledge",
                "relevant_tags": ["significance", "innovation", "approach"]
            },
            {
                "name": "Broader Impacts",
                "description": "How the project benefits society",
                "relevant_tags": ["education", "outreach", "public-health"]
            },
            {
                "name": "Research Plan",
                "description": "Detailed research methodology",
                "relevant_research_questions": ["rq-003"],
                "relevant_tags": ["methods", "tDCS", "cognitive-flexibility"]
            },
            {
                "name": "Preliminary Results",
                "description": "Results from pilot studies",
                "relevant_notes": ["note-003"],
                "relevant_tags": ["pilot", "results", "preliminary"]
            }
        ],
        "required_references": ["wilson2021cognitive"],
        "collaborators": ["Dr. Sarah Johnson", "Dr. Michael Rodriguez"]
    }


@pytest.fixture
def mock_file_system() -> Callable[[Path], None]:
    """Creates a mock file system with a method that populates it with test data.
    
    Returns:
        Callable[[Path], None]: Function to populate a directory with test files
    """
    def populate(base_dir: Path) -> None:
        """Populate a directory with test files mimicking a knowledge base.
        
        Args:
            base_dir: Base directory to populate
        """
        # Create notes
        notes_dir = base_dir / "notes"
        notes_dir.mkdir(exist_ok=True)
        
        note1 = notes_dir / "sleep_deprivation.md"
        note1.write_text("""# Sleep deprivation effects on attention
            
According to [[smith2020neural]], even 24 hours of sleep deprivation can lead to significant decreases in sustained attention. This is relevant to [[rq-001]] as working memory heavily relies on attentional resources.

Key findings:
- 30% decrease in vigilance task performance after 24h without sleep
- Error rates increased progressively with time-on-task
- Recovery required 2 full nights of sleep

This contradicts earlier work by Johnson (2015) who found complete recovery after just one night.""")

        note2 = notes_dir / "hippocampal_aging.md"
        note2.write_text("""# Hippocampal volumetric changes with age

[[brown2019memory]] conducted a longitudinal study showing 1.5% annual hippocampal volume decrease in adults over 65.

This is directly relevant to [[rq-002]] regarding hippocampal volume and memory retention.

Recent findings:
- Volume loss is not uniform across hippocampal subfields
- CA1 region shows earliest atrophy
- Dentate gyrus maintains neurogenesis even in older adults

Need to incorporate these anatomical specifics into our hypothesis.""")

        # Create bibliography
        bib_dir = base_dir / "bibliography"
        bib_dir.mkdir(exist_ok=True)
        
        bib_file = bib_dir / "references.bib"
        bib_file.write_text("""@article{smith2020neural,
  title={Neural mechanisms of cognitive processing},
  author={Smith, John and Johnson, Emily},
  journal={Journal of Neuroscience},
  volume={42},
  number={3},
  pages={1234--1246},
  year={2020},
  publisher={Society for Neuroscience}
}

@article{brown2019memory,
  title={Memory formation in the hippocampus},
  author={Brown, Robert and Davis, Sarah},
  journal={Neurobiology Reviews},
  volume={15},
  number={2},
  pages={87--104},
  year={2019},
  publisher={Academic Press}
}""")

        # Create research questions
        rq_dir = base_dir / "research_questions"
        rq_dir.mkdir(exist_ok=True)
        
        rq_file = rq_dir / "questions.json"
        rq_file.write_text("""[
  {
    "id": "rq-001",
    "question": "How does sleep deprivation affect working memory performance?",
    "hypothesis": "Sleep deprivation will significantly decrease working memory capacity and accuracy.",
    "tags": ["sleep", "working-memory", "cognition"]
  },
  {
    "id": "rq-002",
    "question": "What is the relationship between hippocampal volume and memory retention in older adults?",
    "hypothesis": "Decreased hippocampal volume will correlate with reduced memory retention abilities.",
    "tags": ["hippocampus", "aging", "memory"]
  }
]""")

        # Create templates
        template_dir = base_dir / "templates"
        template_dir.mkdir(exist_ok=True)
        
        template_file = template_dir / "behavioral_experiment.json"
        template_file.write_text("""
{
  "id": "template-behavioral-experiment",
  "name": "Behavioral Experiment Template",
  "fields": [
    {
      "name": "title",
      "type": "string",
      "required": true,
      "description": "Descriptive title of the experiment"
    },
    {
      "name": "research_question",
      "type": "reference",
      "reference_type": "research_question",
      "required": true,
      "description": "The research question this experiment addresses"
    },
    {
      "name": "participants",
      "type": "object",
      "required": true,
      "fields": [
        {"name": "count", "type": "integer", "required": true},
        {"name": "age_range", "type": "string", "required": true},
        {"name": "inclusion_criteria", "type": "string_list", "required": true},
        {"name": "exclusion_criteria", "type": "string_list", "required": true}
      ]
    }
  ]
}""")

        # Create workspaces
        workspace_dir = base_dir / "workspaces"
        workspace_dir.mkdir(exist_ok=True)
        
        workspace_file = workspace_dir / "nsf_grant.json"
        workspace_file.write_text("""{
  "id": "grant-nsf-cognitive",
  "name": "NSF Cognitive Neuroscience Grant 2023",
  "description": "Workspace for preparing NSF grant application on cognitive enhancement techniques",
  "deadline": "2023-06-15",
  "sections": [
    {
      "name": "Project Summary",
      "description": "One-page summary of the proposed research",
      "relevant_tags": ["tDCS", "cognition", "enhancement", "summary"]
    },
    {
      "name": "Intellectual Merit",
      "description": "How the project advances knowledge",
      "relevant_tags": ["significance", "innovation", "approach"]
    }
  ]
}""")
    
    return populate


@pytest.fixture
def mock_collaborator_annotations() -> List[Dict[str, Any]]:
    """Provide sample collaborator annotations for testing collaboration features.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing annotation data
    """
    return [
        {
            "id": "anno-001",
            "collaborator": "Dr. Sarah Johnson",
            "note_id": "note-001",
            "content": "Have you considered the differential effects of sleep deprivation on different components of attention (sustained vs. divided)? This might explain some of the conflicting results in the literature.",
            "created": "2023-01-17T11:20:00"
        },
        {
            "id": "anno-002",
            "collaborator": "Dr. Michael Rodriguez",
            "note_id": "note-002",
            "content": "Our lab has unpublished data showing that exercise might mitigate hippocampal volume loss. This could be an interesting covariate to consider.",
            "created": "2023-02-12T14:05:00"
        },
        {
            "id": "anno-003",
            "collaborator": "Dr. Lisa Chen",
            "note_id": "note-003",
            "content": "Recent work has suggested that 'high-definition' tDCS with smaller electrodes might provide more focal stimulation. Worth considering for your protocol?",
            "created": "2023-03-07T09:30:00"
        }
    ]


@pytest.fixture
def mock_performance_dataset(temp_knowledge_base: Path) -> Path:
    """Create a large dataset for performance testing.
    
    Args:
        temp_knowledge_base: Temporary directory for the knowledge base
        
    Returns:
        Path: Path to the performance test dataset
    """
    dataset_dir = temp_knowledge_base / "performance_test"
    dataset_dir.mkdir()
    
    # Create a large number of notes for performance testing
    notes_dir = dataset_dir / "notes"
    notes_dir.mkdir()
    
    # Generate 100 test notes (for actual testing you might want more)
    for i in range(1, 101):
        note = notes_dir / f"note_{i:04d}.md"
        note.write_text(f"""# Test Note {i}
        
This is test note {i} for performance testing.

It contains references to [[note_{i%100+1:04d}]] and [[note_{(i+5)%100+1:04d}]].

It also cites [[ref_{i%50+1:03d}]].

Tags: #test #performance #tag{i%10+1}
""")
    
    # Create a large bibliography
    bib_dir = dataset_dir / "bibliography"
    bib_dir.mkdir()
    
    bib_content = ""
    for i in range(1, 51):
        bib_content += f"""@article{{ref_{i:03d},
  title={{Performance test reference {i}}},
  author={{Author{i}, Test}},
  journal={{Journal of Testing}},
  volume={{{i}}},
  number={{1}},
  pages={{100--{100+i}}},
  year={{2023}},
  publisher={{Test Publisher}}
}}

"""
    
    bib_file = bib_dir / "performance_refs.bib"
    bib_file.write_text(bib_content)
    
    return dataset_dir
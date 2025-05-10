"""Fixtures for testing the GrowthVault personal development knowledge management system."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from typing import Dict, List, Generator, Tuple, Any, Callable
import json
import datetime


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
        (temp_dir / "sources").mkdir()
        (temp_dir / "habits").mkdir()
        (temp_dir / "values").mkdir()
        (temp_dir / "summaries").mkdir()
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_learning_materials() -> List[Dict[str, Any]]:
    """Provide sample learning materials for testing content ingestion and processing.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing learning material data
    """
    return [
        {
            "id": "book-001",
            "title": "Atomic Habits",
            "author": "James Clear",
            "type": "book",
            "published_date": "2018-10-16",
            "source_text": """# Atomic Habits

## Chapter 1: The Surprising Power of Atomic Habits

The most powerful outcomes are the result of many small changes accumulated over time.
If you want better results, forget about setting goals. Focus on your system instead.
Goals are about the results you want to achieve. Systems are about the processes that lead to those results.

## Key Takeaways:
1. Habits are the compound interest of self-improvement
2. Small habits make a big difference
3. Focus on systems rather than goals
4. Build identity-based habits
5. The two-minute rule: Start with a habit that takes less than two minutes to do

## Actionable Steps:
- Implement habit stacking: After [current habit], I will [new habit]
- Make your habits obvious in your environment
- Focus on becoming the type of person who doesn't miss workouts
- Break down habits into two-minute versions to get started
            """,
            "tags": ["habits", "personal-development", "behavior-change"]
        },
        {
            "id": "article-001",
            "title": "The Power of Deep Work",
            "author": "Cal Newport",
            "type": "article",
            "published_date": "2020-03-15",
            "source_text": """# The Power of Deep Work

In today's distracted world, the ability to focus without interruption is becoming increasingly rare and increasingly valuable.

Deep work is the ability to focus without distraction on a cognitively demanding task. It's a skill that allows you to quickly master complicated information and produce better results in less time.

## Why Deep Work Matters:
- It helps you learn hard things quickly
- It helps you produce at an elite level
- It provides a sense of fulfillment that shallow work cannot

## How to Cultivate Deep Work:
1. Schedule deep work blocks in advance
2. Create a scorecard to track deep work hours
3. Develop a shutdown ritual at the end of each workday
4. Embrace boredom and avoid the constant need for distraction

The ability to perform deep work is becoming increasingly rare precisely at the same time it is becoming increasingly valuable in our economy. As a consequence, the few who cultivate this skill will thrive.
            """,
            "tags": ["productivity", "focus", "work"]
        },
        {
            "id": "podcast-001",
            "title": "The Science of Happiness",
            "author": "Dr. Laurie Santos",
            "type": "podcast",
            "published_date": "2021-05-10",
            "source_text": """# The Science of Happiness Podcast Episode

## Key Points Discussed:

Research consistently shows that happiness isn't about having the perfect life circumstances. Rather, it's about training your mind to perceive and interpret your life in positive ways.

Gratitude practices have been shown to significantly increase baseline happiness. By directing attention to the good things in your life, you literally rewire your brain's attention patterns.

Strong social connections are the strongest predictor of happiness across numerous studies. People who prioritize relationships tend to be happier than those who prioritize financial success or fame.

## Recommendations:
- Write down three new things you're grateful for each day for 21 days
- Meditate for just 10 minutes daily to improve focus and emotional regulation
- Perform random acts of kindness regularly
- Prioritize experiences over material possessions
- Schedule regular social connection time with loved ones
            """,
            "tags": ["happiness", "psychology", "well-being"]
        }
    ]


@pytest.fixture
def sample_personal_values() -> List[Dict[str, Any]]:
    """Provide sample personal values for testing value alignment functionality.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing personal value data
    """
    return [
        {
            "id": "health",
            "name": "Health & Vitality",
            "description": "Physical and mental well-being, energy, and longevity",
            "priority": 1,
            "keywords": ["health", "fitness", "nutrition", "sleep", "exercise", "energy", "well-being", "meditation"]
        },
        {
            "id": "growth",
            "name": "Personal Growth",
            "description": "Continuous learning, skill development, and character improvement",
            "priority": 2,
            "keywords": ["learning", "education", "skills", "development", "improvement", "growth", "books", "courses"]
        },
        {
            "id": "relationships",
            "name": "Meaningful Relationships",
            "description": "Deep connections with family, friends, and community",
            "priority": 3,
            "keywords": ["relationships", "family", "friends", "community", "connection", "social", "communication"]
        },
        {
            "id": "work",
            "name": "Purposeful Work",
            "description": "Career advancement and meaningful contribution through work",
            "priority": 4,
            "keywords": ["career", "work", "job", "business", "productivity", "achievement", "success", "contribution"]
        },
        {
            "id": "finance",
            "name": "Financial Freedom",
            "description": "Building wealth and achieving financial independence",
            "priority": 5,
            "keywords": ["money", "finance", "investing", "saving", "wealth", "budget", "income", "financial"]
        }
    ]


@pytest.fixture
def sample_habits() -> List[Dict[str, Any]]:
    """Provide sample habits for testing habit tracking functionality.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing habit data
    """
    return [
        {
            "id": "habit-001",
            "name": "Daily meditation",
            "description": "Practice mindfulness meditation for mental clarity",
            "target_frequency": {"times": 1, "period": "day"},
            "related_value": "health",
            "source_insights": ["podcast-001"],
            "created_date": "2023-01-15",
            "streak": 12,
            "logs": [
                {"date": "2023-01-15", "completed": True, "notes": "10 minutes"},
                {"date": "2023-01-16", "completed": True, "notes": "15 minutes"},
                {"date": "2023-01-17", "completed": True, "notes": "10 minutes"},
                {"date": "2023-01-18", "completed": True, "notes": "10 minutes"},
                {"date": "2023-01-19", "completed": True, "notes": "12 minutes"},
                {"date": "2023-01-20", "completed": True, "notes": "10 minutes"},
                {"date": "2023-01-21", "completed": True, "notes": "15 minutes"},
                {"date": "2023-01-22", "completed": True, "notes": "10 minutes"},
                {"date": "2023-01-23", "completed": True, "notes": "10 minutes"},
                {"date": "2023-01-24", "completed": True, "notes": "10 minutes"},
                {"date": "2023-01-25", "completed": True, "notes": "12 minutes"},
                {"date": "2023-01-26", "completed": True, "notes": "15 minutes"}
            ]
        },
        {
            "id": "habit-002",
            "name": "Deep work sessions",
            "description": "Focused work without distractions",
            "target_frequency": {"times": 5, "period": "week"},
            "related_value": "work",
            "source_insights": ["article-001"],
            "created_date": "2023-01-10",
            "streak": 3,
            "logs": [
                {"date": "2023-01-10", "completed": True, "notes": "90 minutes"},
                {"date": "2023-01-11", "completed": True, "notes": "120 minutes"},
                {"date": "2023-01-12", "completed": False, "notes": "Interrupted by emergency meeting"},
                {"date": "2023-01-13", "completed": True, "notes": "60 minutes"},
                {"date": "2023-01-16", "completed": True, "notes": "90 minutes"},
                {"date": "2023-01-17", "completed": True, "notes": "120 minutes"}
            ]
        },
        {
            "id": "habit-003",
            "name": "Gratitude journaling",
            "description": "Write three things I'm grateful for",
            "target_frequency": {"times": 1, "period": "day"},
            "related_value": "health",
            "source_insights": ["podcast-001"],
            "created_date": "2023-01-05",
            "streak": 0,
            "logs": [
                {"date": "2023-01-05", "completed": True, "notes": "Family, health, opportunity"},
                {"date": "2023-01-06", "completed": True, "notes": "Friends, learning, comfort"},
                {"date": "2023-01-07", "completed": True, "notes": "Nature, books, rest"},
                {"date": "2023-01-08", "completed": False, "notes": "Forgot - was traveling"},
                {"date": "2023-01-09", "completed": True, "notes": "Travel, experiences, growth"},
                {"date": "2023-01-10", "completed": True, "notes": "Projects, creativity, progress"}
            ]
        }
    ]


@pytest.fixture
def sample_extracted_insights() -> List[Dict[str, Any]]:
    """Provide sample extracted insights for testing insight extraction functionality.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing insight data
    """
    return [
        {
            "id": "insight-001",
            "source_id": "book-001",
            "content": "Habits are the compound interest of self-improvement",
            "type": "principle",
            "related_values": ["growth"],
            "actionability_score": 0.3,
            "tags": ["habits", "improvement"]
        },
        {
            "id": "insight-002",
            "source_id": "book-001",
            "content": "Implement habit stacking: After [current habit], I will [new habit]",
            "type": "action",
            "related_values": ["growth"],
            "actionability_score": 0.9,
            "tags": ["habits", "implementation"]
        },
        {
            "id": "insight-003",
            "source_id": "article-001",
            "content": "Schedule deep work blocks in advance",
            "type": "action",
            "related_values": ["work", "growth"],
            "actionability_score": 0.8,
            "tags": ["productivity", "focus"]
        },
        {
            "id": "insight-004",
            "source_id": "article-001",
            "content": "Deep work helps you learn hard things quickly",
            "type": "principle",
            "related_values": ["growth", "work"],
            "actionability_score": 0.4,
            "tags": ["productivity", "learning"]
        },
        {
            "id": "insight-005",
            "source_id": "podcast-001",
            "content": "Write down three new things you're grateful for each day for 21 days",
            "type": "action",
            "related_values": ["health"],
            "actionability_score": 0.9,
            "tags": ["happiness", "well-being", "gratitude"]
        },
        {
            "id": "insight-006",
            "source_id": "podcast-001",
            "content": "Strong social connections are the strongest predictor of happiness",
            "type": "principle",
            "related_values": ["relationships", "health"],
            "actionability_score": 0.5,
            "tags": ["happiness", "relationships"]
        }
    ]


@pytest.fixture
def sample_progressive_summaries() -> List[Dict[str, Any]]:
    """Provide sample progressive summaries for testing summarization functionality.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing summary data
    """
    return [
        {
            "id": "summary-001",
            "source_id": "book-001",
            "original_length": 1500,
            "layers": [
                {
                    "level": 1,
                    "content": """The most powerful outcomes are the result of many small changes accumulated over time.
If you want better results, forget about setting goals. Focus on your system instead.
Habits are the compound interest of self-improvement.
Small habits make a big difference.
Focus on systems rather than goals.
Build identity-based habits.
The two-minute rule: Start with a habit that takes less than two minutes to do.
Implement habit stacking: After [current habit], I will [new habit].
Make your habits obvious in your environment.
Focus on becoming the type of person who doesn't miss workouts.
Break down habits into two-minute versions to get started.""",
                    "length": 600,
                    "compression_ratio": 0.4
                },
                {
                    "level": 2,
                    "content": """Small changes accumulate into powerful outcomes over time.
Focus on systems instead of goals.
Habits are self-improvement compound interest.
Build identity-based habits.
Two-minute rule: Start with very quick habits.
Habit stacking: Link new habits to existing ones.
Make habits obvious in your environment.""",
                    "length": 300,
                    "compression_ratio": 0.5
                },
                {
                    "level": 3,
                    "content": """System > Goals. Small habits compound.
Identity-based habits stick.
Start tiny (2min). Stack habits.
Make obvious in environment.""",
                    "length": 100,
                    "compression_ratio": 0.33
                }
            ]
        },
        {
            "id": "summary-002",
            "source_id": "article-001",
            "original_length": 1200,
            "layers": [
                {
                    "level": 1,
                    "content": """Deep work is the ability to focus without distraction on a cognitively demanding task.
It helps you learn hard things quickly.
It helps you produce at an elite level.
It provides a sense of fulfillment that shallow work cannot.
Schedule deep work blocks in advance.
Create a scorecard to track deep work hours.
Develop a shutdown ritual at the end of each workday.
Embrace boredom and avoid the constant need for distraction.
The ability to perform deep work is becoming increasingly rare precisely at the same time it is becoming increasingly valuable in our economy.""",
                    "length": 500,
                    "compression_ratio": 0.42
                },
                {
                    "level": 2,
                    "content": """Deep work: focusing without distraction on demanding tasks.
Benefits: learn quickly, produce elite results, find fulfillment.
Strategies: schedule blocks, track hours, establish shutdown ritual, embrace boredom.
Deep work is rare and increasingly valuable.""",
                    "length": 200,
                    "compression_ratio": 0.4
                },
                {
                    "level": 3,
                    "content": """Deep work = distraction-free focus.
Benefits: faster learning, better output, fulfillment.
Schedule, track, shutdown ritual, embrace boredom.""",
                    "length": 120,
                    "compression_ratio": 0.6
                }
            ]
        }
    ]


@pytest.fixture
def sample_source_comparisons() -> Dict[str, Any]:
    """Provide sample source comparisons for testing source comparison functionality.
    
    Returns:
        Dict[str, Any]: Dictionary containing source comparison data
    """
    return {
        "topics": [
            {
                "name": "Habit Formation",
                "sources": [
                    {
                        "id": "book-001",
                        "title": "Atomic Habits",
                        "author": "James Clear",
                        "assertions": [
                            "Focus on systems rather than goals",
                            "Make your habits obvious in your environment",
                            "Small habits compound over time"
                        ]
                    },
                    {
                        "id": "book-hypothetical-1",
                        "title": "The Power of Habit",
                        "author": "Charles Duhigg",
                        "assertions": [
                            "Habits follow a cue-routine-reward loop",
                            "Target the cue and reward to change the routine",
                            "Small habits compound over time"
                        ]
                    },
                    {
                        "id": "book-hypothetical-2",
                        "title": "Tiny Habits",
                        "author": "BJ Fogg",
                        "assertions": [
                            "Start with behaviors that are tiny",
                            "Use existing routines as anchors",
                            "Celebrate immediately after the behavior"
                        ]
                    }
                ],
                "agreements": [
                    {
                        "assertion": "Small habits have significant impacts over time",
                        "sources": ["book-001", "book-hypothetical-1"],
                        "consensus_score": 0.67
                    }
                ],
                "disagreements": [
                    {
                        "topic": "Motivation vs. Environment",
                        "positions": [
                            {
                                "position": "Focus more on environment design",
                                "sources": ["book-001"]
                            },
                            {
                                "position": "Focus more on understanding cue and reward",
                                "sources": ["book-hypothetical-1"]
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Happiness",
                "sources": [
                    {
                        "id": "podcast-001",
                        "title": "The Science of Happiness",
                        "author": "Dr. Laurie Santos",
                        "assertions": [
                            "Gratitude practices increase happiness",
                            "Strong social connections predict happiness",
                            "Experiences provide more happiness than possessions"
                        ]
                    },
                    {
                        "id": "book-hypothetical-3",
                        "title": "Stumbling on Happiness",
                        "author": "Daniel Gilbert",
                        "assertions": [
                            "People are bad at predicting what will make them happy",
                            "Social connections are critical for happiness",
                            "Wealth beyond basic needs provides diminishing returns"
                        ]
                    }
                ],
                "agreements": [
                    {
                        "assertion": "Social connections are crucial for happiness",
                        "sources": ["podcast-001", "book-hypothetical-3"],
                        "consensus_score": 1.0
                    }
                ],
                "disagreements": []
            }
        ]
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
        # Create notes directory
        notes_dir = base_dir / "notes"
        notes_dir.mkdir(exist_ok=True)
        
        note1 = notes_dir / "habit_formation.md"
        note1.write_text("""# Notes on Habit Formation

Building effective habits is crucial for personal development. From my reading, here are the key principles:

## Core Ideas

- Habits are the compound interest of self-improvement
- Small habits make a big difference over time
- Systems matter more than goals
- Habits should be tied to identity changes
- Environment design is crucial for habit maintenance

## Actionable Steps

1. Implement habit stacking with existing routines
2. Make habits obvious through environment design
3. Start with two-minute versions of desired habits
4. Track habits visually
5. Never miss twice

## Sources
- Atomic Habits (James Clear)
- The Power of Habit (Charles Duhigg)
- Tiny Habits (BJ Fogg)

## Life Areas
This connects primarily to my personal growth and health value areas.

## Implementation
I'm currently using these principles to build my meditation and exercise routines.""")

        note2 = notes_dir / "happiness_research.md"
        note2.write_text("""# Happiness Research Summary

## Key Findings

Research on happiness consistently shows several principles:

1. Gratitude practices significantly increase baseline happiness
2. Strong social connections are the strongest predictor of happiness
3. Experiences provide more lasting happiness than material possessions
4. Money improves happiness up to about $75,000 annual income, then shows diminishing returns
5. Helping others boosts personal happiness

## Actionable Practices

- Daily gratitude journaling (3 new things each day)
- Regular social connection time with loved ones
- Meditation for improved attention and emotional regulation
- Random acts of kindness
- Spending on experiences rather than things

## Sources
- The Science of Happiness podcast
- Stumbling on Happiness (Daniel Gilbert)
- The How of Happiness (Sonja Lyubomirsky)

## Life Areas
This connects to my health & vitality and relationships value areas.

## Implementation
I've started daily gratitude journaling and weekly friend gatherings.""")

        # Create sources directory
        sources_dir = base_dir / "sources"
        sources_dir.mkdir(exist_ok=True)
        
        # Create source files
        source1 = sources_dir / "atomic_habits.json"
        source1.write_text("""{
  "id": "book-001",
  "title": "Atomic Habits",
  "author": "James Clear",
  "type": "book",
  "published_date": "2018-10-16",
  "tags": ["habits", "personal-development", "behavior-change"],
  "insights": ["insight-001", "insight-002"]
}""")

        source2 = sources_dir / "deep_work.json"
        source2.write_text("""{
  "id": "article-001",
  "title": "The Power of Deep Work",
  "author": "Cal Newport",
  "type": "article",
  "published_date": "2020-03-15",
  "tags": ["productivity", "focus", "work"],
  "insights": ["insight-003", "insight-004"]
}""")

        # Create habits directory
        habits_dir = base_dir / "habits"
        habits_dir.mkdir(exist_ok=True)
        
        # Create habit files
        habit1 = habits_dir / "meditation.json"
        habit1.write_text("""{
  "id": "habit-001",
  "name": "Daily meditation",
  "description": "Practice mindfulness meditation for mental clarity",
  "target_frequency": {"times": 1, "period": "day"},
  "related_value": "health",
  "source_insights": ["podcast-001"],
  "created_date": "2023-01-15",
  "streak": 12,
  "logs": [
    {"date": "2023-01-15", "completed": true, "notes": "10 minutes"},
    {"date": "2023-01-16", "completed": true, "notes": "15 minutes"}
  ]
}""")

        habit2 = habits_dir / "deep_work.json"
        habit2.write_text("""{
  "id": "habit-002",
  "name": "Deep work sessions",
  "description": "Focused work without distractions",
  "target_frequency": {"times": 5, "period": "week"},
  "related_value": "work",
  "source_insights": ["article-001"],
  "created_date": "2023-01-10",
  "streak": 3,
  "logs": [
    {"date": "2023-01-10", "completed": true, "notes": "90 minutes"},
    {"date": "2023-01-11", "completed": true, "notes": "120 minutes"}
  ]
}""")

        # Create values directory
        values_dir = base_dir / "values"
        values_dir.mkdir(exist_ok=True)
        
        # Create values file
        values_file = values_dir / "personal_values.json"
        values_file.write_text("""{
  "values": [
    {
      "id": "health",
      "name": "Health & Vitality",
      "description": "Physical and mental well-being, energy, and longevity",
      "priority": 1,
      "keywords": ["health", "fitness", "nutrition", "sleep", "exercise", "energy", "well-being", "meditation"]
    },
    {
      "id": "growth",
      "name": "Personal Growth",
      "description": "Continuous learning, skill development, and character improvement",
      "priority": 2,
      "keywords": ["learning", "education", "skills", "development", "improvement", "growth", "books", "courses"]
    }
  ]
}""")

        # Create summaries directory
        summaries_dir = base_dir / "summaries"
        summaries_dir.mkdir(exist_ok=True)
        
        # Create summary files
        summary1 = summaries_dir / "atomic_habits_summary.json"
        summary1.write_text("""{
  "id": "summary-001",
  "source_id": "book-001",
  "original_length": 1500,
  "layers": [
    {
      "level": 1,
      "content": "The most powerful outcomes are the result of many small changes accumulated over time.\\nIf you want better results, forget about setting goals. Focus on your system instead.\\nHabits are the compound interest of self-improvement.\\nSmall habits make a big difference.\\nFocus on systems rather than goals.\\nBuild identity-based habits.\\nThe two-minute rule: Start with a habit that takes less than two minutes to do.\\nImplement habit stacking: After [current habit], I will [new habit].\\nMake your habits obvious in your environment.\\nFocus on becoming the type of person who doesn't miss workouts.\\nBreak down habits into two-minute versions to get started.",
      "length": 600,
      "compression_ratio": 0.4
    },
    {
      "level": 2,
      "content": "Small changes accumulate into powerful outcomes over time.\\nFocus on systems instead of goals.\\nHabits are self-improvement compound interest.\\nBuild identity-based habits.\\nTwo-minute rule: Start with very quick habits.\\nHabit stacking: Link new habits to existing ones.\\nMake habits obvious in your environment.",
      "length": 300,
      "compression_ratio": 0.5
    }
  ]
}""")
    
    return populate


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
    
    # Create notes directory
    notes_dir = dataset_dir / "notes"
    notes_dir.mkdir()
    
    # Generate 100 test notes for performance testing
    for i in range(1, 101):
        note = notes_dir / f"note_{i:04d}.md"
        content = f"""# Test Note {i}

## Summary
This is test note {i} for performance testing.

## Related Notes
- Note {(i+1)%100+1:04d}
- Note {(i+5)%100+1:04d}
- Note {(i+10)%100+1:04d}

## Sources
- Source {i%20+1:03d}
- Source {(i+3)%20+1:03d}

## Tags
#test #performance #tag{i%10+1}

## Life Areas
- {["Health", "Growth", "Relationships", "Work", "Finance"][i%5]}
- {["Health", "Growth", "Relationships", "Work", "Finance"][(i+2)%5]}
"""
        note.write_text(content)
    
    # Create sources directory
    sources_dir = dataset_dir / "sources"
    sources_dir.mkdir()
    
    # Generate 20 test sources
    for i in range(1, 21):
        source = sources_dir / f"source_{i:03d}.json"
        source_content = {
            "id": f"source-{i:03d}",
            "title": f"Test Source {i}",
            "author": f"Author {i}",
            "type": ["book", "article", "podcast", "video", "course"][i%5],
            "published_date": f"2023-{i%12+1:02d}-{i%28+1:02d}",
            "tags": ["test", "performance", f"topic-{i%10+1}"],
            "insights": [f"insight-{i*10+j:03d}" for j in range(1, 6)]
        }
        source.write_text(json.dumps(source_content, indent=2))
    
    # Create insights directory
    insights_dir = dataset_dir / "insights"
    insights_dir.mkdir()
    
    # Generate 200 test insights
    for i in range(1, 201):
        insight = insights_dir / f"insight_{i:03d}.json"
        insight_content = {
            "id": f"insight-{i:03d}",
            "source_id": f"source-{(i//10)+1:03d}",
            "content": f"This is test insight {i} for performance testing.",
            "type": ["principle", "action", "concept", "example", "reflection"][i%5],
            "related_values": [["health", "growth", "relationships", "work", "finance"][i%5]],
            "actionability_score": round(((i%10)+1)/10, 1),
            "tags": ["test", f"topic-{i%10+1}", f"tag-{i%5+1}"]
        }
        insight.write_text(json.dumps(insight_content, indent=2))
    
    # Create habits directory
    habits_dir = dataset_dir / "habits"
    habits_dir.mkdir()
    
    # Generate 30 test habits
    for i in range(1, 31):
        habit = habits_dir / f"habit_{i:03d}.json"
        today = datetime.date.today()
        logs = []
        for j in range(1, 15):
            log_date = today - datetime.timedelta(days=j)
            logs.append({
                "date": log_date.isoformat(),
                "completed": j % 3 != 0,  # Complete 2/3 of the time
                "notes": f"Test log entry {j} for habit {i}"
            })
        
        habit_content = {
            "id": f"habit-{i:03d}",
            "name": f"Test Habit {i}",
            "description": f"This is test habit {i} for performance testing.",
            "target_frequency": {"times": i%7+1, "period": ["day", "week", "month"][i%3]},
            "related_value": ["health", "growth", "relationships", "work", "finance"][i%5],
            "source_insights": [f"insight-{i*5+j:03d}" for j in range(1, 4)],
            "created_date": (today - datetime.timedelta(days=15)).isoformat(),
            "streak": i % 10,
            "logs": logs
        }
        habit.write_text(json.dumps(habit_content, indent=2))
    
    return dataset_dir
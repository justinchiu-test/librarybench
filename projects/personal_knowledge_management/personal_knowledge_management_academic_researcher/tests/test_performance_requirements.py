"""Tests to verify the system meets performance requirements."""

import os
import time
import tempfile
import shutil
from pathlib import Path
from uuid import uuid4

import pytest
import networkx as nx

from researchbrain.core.brain import ResearchBrain
from researchbrain.core.models import (
    Citation, EvidenceStrength, EvidenceType, Note, ResearchQuestion
)


class TestPerformanceRequirements:
    """Tests to verify the system meets performance requirements."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Fixture that creates a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def empty_brain(self, temp_data_dir):
        """Fixture that creates an empty ResearchBrain instance."""
        return ResearchBrain(temp_data_dir)
    
    def _create_large_dataset(self, brain, note_count=1000):
        """Create a large dataset for performance testing.
        
        Args:
            brain: ResearchBrain instance
            note_count: Number of notes to create (default: 1000)
        """
        # Create citations
        citation_count = int(note_count / 10)  # 1 citation per 10 notes
        citation_ids = []
        for i in range(citation_count):
            citation_id = brain.create_citation(
                title=f"Citation {i}",
                authors=[f"Author {i}"],
                year=2020 + (i % 5),
                journal=f"Journal {i % 20}",
                abstract=f"Abstract for citation {i}" * 5
            )
            citation_ids.append(citation_id)
        
        # Create notes with links to citations
        note_ids = []
        for i in range(note_count):
            content = f"Content for note {i}. "
            
            # Add citation references
            citations_to_reference = min(5, len(citation_ids))
            for j in range(citations_to_reference):
                idx = (i + j) % len(citation_ids)
                content += f"This references citation [@citation{idx}]. "
            
            # Make content longer
            content += f"Additional content for note {i}. " * 10
            
            note_id = brain.create_note(
                title=f"Note {i}",
                content=content,
                tags={f"tag{i % 50}", f"category{i % 10}"}
            )
            note_ids.append(note_id)
            
            # Link to citations
            citations_to_link = min(3, len(citation_ids))
            for j in range(citations_to_link):
                idx = (i + j) % len(citation_ids)
                brain.link_note_to_paper(note_id, citation_ids[idx])
        
        # Create research questions
        question_count = int(note_count / 50)  # 1 question per 50 notes
        for i in range(question_count):
            question_id = brain.create_research_question(
                question=f"Research question {i}?",
                description=f"Description for question {i}" * 3,
                priority=i % 10
            )
            
            # Add evidence from notes
            evidence_count = min(10, len(note_ids))
            for j in range(evidence_count):
                idx = (i * 10 + j) % len(note_ids)
                evidence_type = EvidenceType.SUPPORTING if j % 3 != 0 else EvidenceType.CONTRADICTING
                strength = EvidenceStrength.STRONG if j % 2 == 0 else EvidenceStrength.MODERATE
                
                brain.add_evidence_to_question(
                    question_id=question_id,
                    note_id=note_ids[idx],
                    evidence_type=evidence_type,
                    strength=strength,
                    description=f"Evidence {j} for question {i}"
                )
        
        return {
            "note_count": note_count,
            "citation_count": citation_count,
            "question_count": question_count,
            "note_ids": note_ids,
            "citation_ids": citation_ids
        }
    
    @pytest.mark.performance
    def test_note_linking_performance(self, empty_brain):
        """Test that note linking operations complete in under 500ms."""
        # Create test data
        citation_id = empty_brain.create_citation(
            title="Test Citation",
            authors=["Test Author"],
            year=2023
        )
        
        # Measure time for single linking operation
        start_time = time.time()
        
        note_id = empty_brain.create_note(
            title="Test Note",
            content="Test content"
        )
        empty_brain.link_note_to_paper(note_id, citation_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Assert that the operation completes in under 500ms
        assert duration < 0.5, f"Note linking operation took {duration:.4f} seconds, which exceeds the requirement of 0.5 seconds"
        
        # Test bulk linking performance (100 notes to same citation)
        start_time = time.time()
        
        note_ids = []
        for i in range(100):
            note_id = empty_brain.create_note(
                title=f"Bulk Test Note {i}",
                content=f"Bulk test content {i}"
            )
            empty_brain.link_note_to_paper(note_id, citation_id)
            note_ids.append(note_id)
        
        end_time = time.time()
        total_duration = end_time - start_time
        per_operation_duration = total_duration / 100
        
        # Assert that each operation averages under 500ms
        assert per_operation_duration < 0.5, f"Average note linking operation took {per_operation_duration:.4f} seconds, which exceeds the requirement of 0.5 seconds"
    
    @pytest.mark.performance
    def test_citation_processing_rate(self, empty_brain, tmp_path):
        """Test that citation link generation processes at least 100 papers per minute."""
        # Create test bibtex files for bulk import
        files_to_create = 100
        file_paths = []
        
        for i in range(files_to_create):
            file_path = tmp_path / f"citation_{i}.bib"
            with open(file_path, "w") as f:
                f.write(f"""
@article{{test{i}2023,
  title={{Test Paper Title {i}}},
  author={{Test Author and Another Author}},
  journal={{Test Journal}},
  year={{2023}},
  volume={{1}},
  number={{1}},
  pages={{1--10}}
}}
                """)
            file_paths.append(file_path)
        
        # Measure time to process all citations
        start_time = time.time()
        
        citation_ids = []
        for file_path in file_paths:
            citation_id = empty_brain.import_paper(file_path)
            citation_ids.append(citation_id)
        
        end_time = time.time()
        duration = end_time - start_time
        papers_per_minute = (files_to_create / duration) * 60
        
        # Assert that the processing rate is at least 100 papers per minute
        assert papers_per_minute >= 100, f"Citation processing rate is {papers_per_minute:.2f} papers per minute, which is below the requirement of 100 papers per minute"
    
    @pytest.mark.performance
    def test_search_performance(self, empty_brain):
        """Test that full-text search returns results in under 2 seconds."""
        # Create a large dataset with 1000 notes
        self._create_large_dataset(empty_brain, note_count=1000)
        
        # Measure search time
        start_time = time.time()
        
        results = empty_brain.search("content")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Assert that search completes in under 2 seconds
        assert duration < 2.0, f"Search operation took {duration:.4f} seconds, which exceeds the requirement of 2.0 seconds"
        
        # Verify search found results
        total_results = sum(len(items) for items in results.values())
        assert total_results > 0, "Search didn't find any results"
    
    @pytest.mark.performance
    def test_large_collection_handling(self, empty_brain):
        """Test efficient handling of large note collections (10,000+)."""
        # Skip this test unless explicitly enabled for performance testing
        if not os.environ.get("RUN_LARGE_PERFORMANCE_TESTS"):
            pytest.skip("Skipping large collection test. Set RUN_LARGE_PERFORMANCE_TESTS=1 to run.")
        
        # Create a large dataset with 10,000 notes
        dataset = self._create_large_dataset(empty_brain, note_count=10000)
        
        # Verify the size of the dataset
        assert len(dataset["note_ids"]) == 10000, f"Expected 10,000 notes but got {len(dataset['note_ids'])}"
        
        # Test operations on the large collection
        
        # 1. Test retrieval time
        start_time = time.time()
        for i in range(100):  # Sample 100 random notes
            idx = (i * 100) % 10000
            note = empty_brain.get_note(dataset["note_ids"][idx])
            assert note is not None
        retrieval_time = time.time() - start_time
        avg_retrieval_time = retrieval_time / 100
        
        # Assert average retrieval time is under 100ms
        assert avg_retrieval_time < 0.1, f"Average note retrieval time is {avg_retrieval_time:.4f} seconds, which is too slow for large collections"
        
        # 2. Test search time
        start_time = time.time()
        results = empty_brain.search("content")
        search_time = time.time() - start_time
        
        # Assert search time is under 2 seconds
        assert search_time < 2.0, f"Search on large collection took {search_time:.4f} seconds, exceeding the requirement of 2.0 seconds"
        
        # 3. Test knowledge graph operations
        start_time = time.time()
        for i in range(100):  # Sample 100 random notes
            idx = (i * 100) % 10000
            related = empty_brain.get_related_nodes(dataset["note_ids"][idx])
        graph_time = time.time() - start_time
        avg_graph_time = graph_time / 100
        
        # Assert average graph operation time is under 100ms
        assert avg_graph_time < 0.1, f"Average graph operation time is {avg_graph_time:.4f} seconds, which is too slow for large collections"
    
    @pytest.mark.performance
    def test_knowledge_graph_scaling(self, empty_brain):
        """Test that the knowledge graph maintains performance with growing size."""
        # Create datasets of increasing size and measure performance
        sizes = [100, 500, 1000, 2000]
        times = []
        
        for size in sizes:
            # Create dataset
            dataset = self._create_large_dataset(empty_brain, note_count=size)
            
            # Measure time for a standard operation (getting related nodes)
            start_time = time.time()
            for i in range(10):  # Sample 10 random notes
                idx = (i * 10) % size
                related = empty_brain.get_related_nodes(dataset["note_ids"][idx])
            end_time = time.time()
            
            operation_time = (end_time - start_time) / 10  # Average time per operation
            times.append(operation_time)
            
            # Clear data for next iteration
            empty_brain = ResearchBrain(tempfile.mkdtemp())
        
        # Check that performance doesn't degrade super-linearly
        # The time for the largest dataset should be less than (largest/smallest)^2 times the time for the smallest
        ratio = sizes[-1] / sizes[0]  # Ratio of largest to smallest dataset
        time_ratio = times[-1] / times[0]  # Ratio of time for largest to smallest
        
        assert time_ratio < ratio * 2, f"Performance degradation is super-linear: time ratio {time_ratio:.2f} exceeds acceptable threshold of {ratio * 2:.2f}"
    
    @pytest.mark.performance
    def test_memory_efficiency(self, empty_brain):
        """Test that the system operates efficiently within reasonable memory constraints."""
        import psutil
        import gc
        
        # Force garbage collection to get a clean baseline
        gc.collect()
        
        # Get baseline memory usage
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Create a moderate-sized dataset (5000 notes)
        dataset = self._create_large_dataset(empty_brain, note_count=5000)
        
        # Force garbage collection
        gc.collect()
        
        # Get memory usage after creating dataset
        dataset_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_per_note = (dataset_memory - baseline_memory) / 5000  # MB per note
        
        # Assert memory usage per note is reasonable (should be a few KB per note)
        assert memory_per_note < 0.1, f"Memory usage per note is {memory_per_note:.4f} MB, which exceeds reasonable memory constraints"
        
        # Verify total memory usage is within workstation constraints (less than 1 GB for 5000 notes)
        assert dataset_memory - baseline_memory < 1000, f"Total memory usage for 5000 notes is {dataset_memory - baseline_memory:.2f} MB, which exceeds reasonable workstation constraints"
    
    @pytest.mark.performance
    def test_multiple_concurrent_operations(self, empty_brain):
        """Test system performance during multiple concurrent operations."""
        import threading
        
        # Create initial dataset
        dataset = self._create_large_dataset(empty_brain, note_count=1000)
        
        # Define operations to run concurrently
        def create_notes():
            for i in range(50):
                empty_brain.create_note(
                    title=f"Concurrent Note {i}",
                    content=f"Content for concurrent note {i}"
                )
        
        def search_content():
            for i in range(5):
                empty_brain.search(f"note {i*100}")
        
        def get_related():
            for i in range(50):
                idx = i % len(dataset["note_ids"])
                empty_brain.get_related_nodes(dataset["note_ids"][idx])
        
        # Measure time for sequential operations
        start_time = time.time()
        create_notes()
        search_content()
        get_related()
        sequential_time = time.time() - start_time
        
        # Reinitialize brain
        empty_brain = ResearchBrain(tempfile.mkdtemp())
        dataset = self._create_large_dataset(empty_brain, note_count=1000)
        
        # Measure time for concurrent operations
        start_time = time.time()
        threads = [
            threading.Thread(target=create_notes),
            threading.Thread(target=search_content),
            threading.Thread(target=get_related)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        concurrent_time = time.time() - start_time
        
        # The system should handle concurrent operations efficiently
        assert concurrent_time < sequential_time, f"Concurrent operations took {concurrent_time:.4f} seconds, which is slower than sequential operations ({sequential_time:.4f} seconds)"
    
    @pytest.mark.performance
    def test_data_integrity_during_concurrent_operations(self, empty_brain):
        """Test that data integrity is maintained during concurrent operations."""
        import threading
        import random
        
        # Create initial dataset
        dataset = self._create_large_dataset(empty_brain, note_count=100)
        
        # Create a shared counter for successful operations
        class Counter:
            def __init__(self):
                self.value = 0
                self.lock = threading.Lock()
            
            def increment(self):
                with self.lock:
                    self.value += 1
        
        counter = Counter()
        
        # Define operations with data verification
        def update_notes():
            for i in range(20):
                idx = random.randint(0, len(dataset["note_ids"]) - 1)
                note_id = dataset["note_ids"][idx]
                
                # Read current content
                note = empty_brain.get_note(note_id)
                if note:
                    original_content = note.content
                    new_content = original_content + f"\nUpdated in thread at {time.time()}"
                    
                    # Update the note
                    success = empty_brain.update_note(
                        note_id=note_id,
                        content=new_content
                    )
                    
                    # Verify the update
                    if success:
                        updated_note = empty_brain.get_note(note_id)
                        if updated_note and updated_note.content == new_content:
                            counter.increment()
        
        def create_and_link():
            for i in range(20):
                # Create a note
                note_id = empty_brain.create_note(
                    title=f"Concurrent Link Note {i}",
                    content=f"Content for concurrent link note {i}"
                )
                
                # Link to a random citation
                idx = random.randint(0, len(dataset["citation_ids"]) - 1)
                citation_id = dataset["citation_ids"][idx]
                
                success = empty_brain.link_note_to_paper(note_id, citation_id)
                
                # Verify the link
                if success:
                    note = empty_brain.get_note(note_id)
                    if note and citation_id in note.citations:
                        counter.increment()
        
        # Run concurrent operations
        threads = [
            threading.Thread(target=update_notes),
            threading.Thread(target=update_notes),
            threading.Thread(target=create_and_link),
            threading.Thread(target=create_and_link)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify that most operations succeeded (at least 70%)
        expected_total = 80  # 20 operations per thread × 4 threads
        success_rate = counter.value / expected_total
        
        assert success_rate >= 0.7, f"Only {counter.value} out of {expected_total} operations succeeded ({success_rate:.2%}), which indicates data integrity issues during concurrent operations"
    
    @pytest.mark.performance
    def test_recovery_from_interruption(self, empty_brain, temp_data_dir):
        """Test that the system can recover from interruptions without data loss."""
        # Create dataset
        dataset = self._create_large_dataset(empty_brain, note_count=100)
        
        # Get some IDs to verify after recovery
        note_id = dataset["note_ids"][0]
        citation_id = dataset["citation_ids"][0]
        
        # Verify data exists
        note = empty_brain.get_note(note_id)
        citation = empty_brain.storage.get(Citation, citation_id)
        
        assert note is not None
        assert citation is not None
        
        original_note_content = note.content
        
        # Simulate an interruption by creating a new instance without proper shutdown
        del empty_brain
        
        # Create a new instance using the same data directory
        recovered_brain = ResearchBrain(temp_data_dir)
        
        # Verify data persisted
        recovered_note = recovered_brain.get_note(note_id)
        recovered_citation = recovered_brain.storage.get(Citation, citation_id)
        
        assert recovered_note is not None, "Failed to recover note after interruption"
        assert recovered_citation is not None, "Failed to recover citation after interruption"
        
        # Verify content integrity
        assert recovered_note.content == original_note_content, "Note content changed during recovery"
        
        # Verify knowledge graph was rebuilt
        assert recovered_brain._knowledge_graph.has_node(str(note_id)), "Knowledge graph missing note node after recovery"
        assert recovered_brain._knowledge_graph.has_node(str(citation_id)), "Knowledge graph missing citation node after recovery"
        
        # Verify the system can continue operations after recovery
        new_note_id = recovered_brain.create_note(
            title="Post-Recovery Note",
            content="This note was created after recovery from interruption"
        )
        
        assert recovered_brain.get_note(new_note_id) is not None, "Failed to create new note after recovery"
"""Performance tests for the analyzer."""

import time
import tempfile
from pathlib import Path
from legacy_analyzer import LegacyAnalyzer


class TestPerformance:
    """Test performance requirements."""

    def test_analyze_100k_lines_under_10_minutes(self):
        """Test analyzing 100,000 lines of code in under 10 minutes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Generate a codebase with ~100k lines
            num_modules = 100
            lines_per_module = 1000

            for i in range(num_modules):
                module_dir = base_path / f"module_{i}"
                module_dir.mkdir()

                # Create files with realistic code
                for j in range(5):  # 5 files per module
                    file_content = f'''"""Module {i} File {j}"""
import os
import sys
import json
from typing import List, Dict

class Service_{i}_{j}:
    """Service class with many methods."""
    
    def __init__(self):
        self.data = {{}}
        self.connections = []
'''
                    # Add methods to reach line count
                    for k in range(lines_per_module // 25):  # ~40 methods
                        file_content += f'''
    def method_{k}(self, param1: str, param2: int) -> Dict:
        """Method {k} documentation."""
        result = {{}}
        for i in range(10):
            if i % 2 == 0:
                result[str(i)] = param1
            else:
                result[str(i)] = param2
        return result
'''

                    (module_dir / f"service_{j}.py").write_text(file_content)

            # Time the analysis
            analyzer = LegacyAnalyzer()
            start_time = time.time()

            result = analyzer.analyze_codebase(str(base_path), generate_roadmap=False)

            duration = time.time() - start_time

            # Should complete in under 10 minutes (600 seconds)
            assert duration < 600

            # Should have analyzed all modules
            assert result.summary["total_modules"] >= num_modules * 5
            assert result.summary["total_lines_of_code"] >= 90000  # Allow some variance

    def test_generate_extraction_plans_for_50_modules(self):
        """Test generating extraction plans for 50 modules in under 5 minutes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create 50 interconnected modules
            modules = []
            for i in range(50):
                module_name = f"service_{i}.py"
                modules.append(module_name)

                # Create dependencies to other modules
                deps = [
                    f"service_{j}"
                    for j in range(max(0, i - 5), min(50, i + 5))
                    if j != i
                ]

                content = f'''"""Service module {i}"""
'''
                for dep in deps[:3]:  # Import up to 3 dependencies
                    content += f"from {dep} import Service\n"

                content += f"""
class Service_{i}:
    def __init__(self):
        self.id = {i}
        
    def process(self):
        pass
"""

                (base_path / module_name).write_text(content)

            # Time the extraction analysis
            analyzer = LegacyAnalyzer()
            start_time = time.time()

            result = analyzer.analyze_codebase(
                str(base_path), generate_roadmap=False, modules_to_extract=modules
            )

            duration = time.time() - start_time

            # Should complete in under 5 minutes (300 seconds)
            assert duration < 300

            # Should have analyzed requested modules
            assert len(result.extraction_feasibilities) > 0

    def test_detect_database_coupling_in_1000_files(self):
        """Test detecting database coupling in 1,000 files in under 2 minutes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create 1000 files with varying database access patterns
            for i in range(1000):
                # Some files have database access
                if i % 3 == 0:
                    content = f'''"""Module with database access"""
import sqlalchemy
from sqlalchemy import create_engine

class DataService_{i}:
    __tablename__ = 'table_{i % 10}'
    
    def get_data(self):
        query = "SELECT * FROM table_{i % 10} WHERE status = 'active'"
        return self.execute(query)
        
    def update_data(self, id, data):
        query = f"UPDATE table_{i % 10} SET data = '{{data}}' WHERE id = {{id}}"
        return self.execute(query)
'''
                else:
                    content = f'''"""Regular module {i}"""
class Service_{i}:
    def process(self):
        return "processing"
'''

                (base_path / f"module_{i}.py").write_text(content)

            # Time the database coupling detection
            analyzer = LegacyAnalyzer()
            start_time = time.time()

            # Just analyze database coupling
            detector = analyzer.db_coupling_detector
            couplings = detector.analyze_database_coupling(str(base_path))

            duration = time.time() - start_time

            # Should complete in under 2 minutes (120 seconds)
            assert duration < 120

            # Should find database couplings
            assert len(couplings) > 0

    def test_create_roadmap_under_60_seconds(self):
        """Test creating modernization roadmaps in under 60 seconds."""
        # Create pre-analyzed data
        from legacy_analyzer.models import (
            LegacyPattern,
            PatternType,
            ModernizationDifficulty,
            RiskLevel,
            StranglerFigBoundary,
            ExtractionFeasibility,
            DatabaseCoupling,
        )

        # Generate substantial test data
        patterns = []
        for i in range(50):
            patterns.append(
                LegacyPattern(
                    pattern_type=PatternType.GOD_CLASS,
                    module_path=f"module_{i}.py",
                    description=f"Pattern {i}",
                    difficulty=ModernizationDifficulty.HIGH,
                    risk=RiskLevel.HIGH,
                    affected_files=[f"module_{i}.py"],
                    metrics={"complexity": 50 + i},
                )
            )

        boundaries = []
        for i in range(20):
            boundaries.append(
                StranglerFigBoundary(
                    boundary_name=f"boundary_{i}",
                    internal_modules=[
                        f"module_{j}.py" for j in range(i * 5, (i + 1) * 5)
                    ],
                    external_dependencies=["external"],
                    internal_dependencies=[],
                    api_surface=[f"module_{i * 5}.py"],
                    isolation_score=0.7,
                    recommended_order=i,
                    estimated_effort_hours=100,
                )
            )

        feasibilities = []
        for i in range(30):
            feasibilities.append(
                ExtractionFeasibility(
                    module_path=f"module_{i}.py",
                    feasibility_score=0.5 + (i * 0.01),
                    dependencies_to_break=["dep1", "dep2"],
                    backward_compatibility_requirements=["req1"],
                    estimated_effort_hours=50,
                    risks=["risk1"],
                    recommendations=["rec1", "rec2"],
                )
            )

        couplings = []
        for i in range(10):
            couplings.append(
                DatabaseCoupling(
                    coupled_modules=[f"module_{i}.py", f"module_{i + 1}.py"],
                    shared_tables=[f"table_{i}"],
                    orm_models=[],
                    coupling_strength=0.7,
                    decoupling_effort_hours=40,
                )
            )

        # Time roadmap generation
        from legacy_analyzer.roadmap_generator import RoadmapGenerator

        generator = RoadmapGenerator()

        start_time = time.time()

        roadmap = generator.generate_roadmap(
            "Performance Test Project", patterns, boundaries, feasibilities, couplings
        )

        duration = time.time() - start_time

        # Should complete in under 60 seconds
        assert duration < 60

        # Should generate complete roadmap
        assert roadmap is not None
        assert len(roadmap.phases) > 0
        assert roadmap.total_duration_days > 0

    def test_incremental_analysis(self):
        """Test that pattern detection works incrementally."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create initial set of files
            for i in range(10):
                (base_path / f"module_{i}.py").write_text(f"""
class Service_{i}:
    def method(self):
        pass
""")

            analyzer = LegacyAnalyzer()

            # First analysis
            start_time = time.time()
            result1 = analyzer.analyze_codebase(str(base_path), generate_roadmap=False)
            first_duration = time.time() - start_time

            # Add more files
            for i in range(10, 20):
                (base_path / f"module_{i}.py").write_text(f"""
class Service_{i}:
    def method(self):
        pass
""")

            # Second analysis should complete reasonably fast
            start_time = time.time()
            result2 = analyzer.analyze_codebase(str(base_path), generate_roadmap=False)
            second_duration = time.time() - start_time

            # Both should complete quickly for small codebases
            assert first_duration < 5
            assert second_duration < 10

            # Should analyze more modules in second run
            assert result2.summary["total_modules"] > result1.summary["total_modules"]

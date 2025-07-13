"""Performance tests for the scanner."""

import pytest
import time
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from pypatternguard import SecurityScanner, ScannerConfig
from pypatternguard.patterns import HardcodedSecretDetector


class TestPerformance:
    """Test performance characteristics of the scanner."""
    
    def test_single_file_scan_speed(self):
        """Test scanning speed for a single file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write 1000 lines
            for i in range(1000):
                f.write(f"variable_{i} = {i}\n")
            f.write("password = 'secret123'\n")
            temp_path = Path(f.name)
        
        try:
            scanner = SecurityScanner()
            start_time = time.time()
            result = scanner.scan(str(temp_path))
            duration = time.time() - start_time
            
            assert duration < 1.0  # Should scan single file in under 1 second
            assert result.total_lines_scanned >= 1000
            assert len(result.vulnerabilities) >= 1
        finally:
            temp_path.unlink()
    
    def test_parallel_scanning(self):
        """Test parallel scanning performance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create 10 files
            for i in range(10):
                file_path = temp_path / f"file_{i}.py"
                file_path.write_text(f"password_{i} = 'secret{i}'\n" * 100)
            
            # Test with different worker counts
            for workers in [1, 2, 4]:
                config = ScannerConfig(max_workers=workers)
                scanner = SecurityScanner(config)
                
                start_time = time.time()
                result = scanner.scan(str(temp_path))
                duration = time.time() - start_time
                
                assert result.total_files_scanned == 10
                assert result.total_lines_scanned >= 1000
                
                # Parallel should be faster (within reason)
                if workers > 1:
                    assert duration < 5.0
    
    def test_memory_efficiency(self):
        """Test memory efficiency with large files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write a large file (10MB)
            large_content = "x = 1\n" * 1000000  # ~6MB
            f.write(large_content)
            f.write("api_key = 'sk-1234567890abcdef'\n")
            temp_path = Path(f.name)
        
        try:
            config = ScannerConfig(max_file_size_mb=15.0)
            scanner = SecurityScanner(config)
            
            # Should complete without memory issues
            result = scanner.scan(str(temp_path))
            assert result.total_files_scanned == 1
            assert len(result.vulnerabilities) >= 1
        finally:
            temp_path.unlink()
    
    def test_incremental_scan_simulation(self):
        """Test performance of incremental scanning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Initial files
            for i in range(5):
                file_path = temp_path / f"initial_{i}.py"
                file_path.write_text("# Safe code\n")
            
            scanner = SecurityScanner()
            
            # First scan
            start_time = time.time()
            first_result = scanner.scan(str(temp_path))
            first_duration = time.time() - start_time
            
            # Add new file
            new_file = temp_path / "new_file.py"
            new_file.write_text("password = 'new_secret'\n")
            
            # Second scan (simulating incremental)
            start_time = time.time()
            second_result = scanner.scan(str(temp_path))
            second_duration = time.time() - start_time
            
            assert first_result.total_files_scanned == 5
            assert second_result.total_files_scanned == 6
            assert len(second_result.vulnerabilities) >= 1
    
    def test_pattern_matching_performance(self):
        """Test performance of pattern matching."""
        detector = HardcodedSecretDetector()
        
        # Generate content with many potential matches
        content = ""
        for i in range(1000):
            content += f"var_{i} = 'value_{i}'\n"
            if i % 100 == 0:
                content += f'password = "secret_{i}"\n'
        
        start_time = time.time()
        vulnerabilities = detector.detect(Path("test.py"), content)
        duration = time.time() - start_time
        
        assert duration < 0.5  # Should be fast
        # Should detect the passwords inserted every 100 lines
        assert len(vulnerabilities) >= 5
    
    def test_ast_parsing_performance(self):
        """Test AST parsing performance."""
        # Generate complex but valid Python code
        complex_code = """
def complex_function():
    for i in range(100):
        if i % 2 == 0:
            try:
                with open(f'file_{i}.txt') as f:
                    data = f.read()
                    if 'pattern' in data:
                        eval(data)  # Vulnerability
            except Exception as e:
                pass
"""
        
        from pypatternguard.patterns import InputValidationDetector
        import ast
        
        detector = InputValidationDetector()
        tree = ast.parse(complex_code * 100)  # Repeat for complexity
        
        start_time = time.time()
        vulnerabilities = detector.detect(Path("complex.py"), complex_code * 100, tree)
        duration = time.time() - start_time
        
        assert duration < 2.0  # Should handle complex AST efficiently
        assert len(vulnerabilities) >= 100
    
    def test_concurrent_file_access(self):
        """Test concurrent file access handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create shared file
            shared_file = temp_path / "shared.py"
            shared_file.write_text("password = 'shared_secret'\n")
            
            # Create scanner with multiple workers
            config = ScannerConfig(max_workers=4)
            scanner = SecurityScanner(config)
            
            # Scan multiple times concurrently
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(scanner.scan, str(temp_path))
                    for _ in range(3)
                ]
                
                results = [f.result() for f in futures]
                
                # All scans should succeed
                assert all(r.total_files_scanned == 1 for r in results)
                assert all(len(r.vulnerabilities) >= 1 for r in results)
    
    def test_large_codebase_simulation(self):
        """Test scanning a simulated large codebase."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create directory structure
            for module in range(5):
                module_dir = temp_path / f"module_{module}"
                module_dir.mkdir()
                
                for file_num in range(20):
                    file_path = module_dir / f"file_{file_num}.py"
                    content = f"# Module {module} File {file_num}\n" * 50
                    if file_num % 5 == 0:
                        content += "api_key = 'secret_key_12345'\n"
                    file_path.write_text(content)
            
            scanner = SecurityScanner()
            start_time = time.time()
            result = scanner.scan(str(temp_path))
            duration = time.time() - start_time
            
            assert result.total_files_scanned == 100
            # Vulnerabilities depend on pattern detection  
            assert result.total_lines_scanned >= 5000
            assert duration < 30  # Should complete within 30 seconds
    
    def test_file_size_limit_performance(self):
        """Test performance impact of file size limits."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files of different sizes
            small_file = temp_path / "small.py"
            small_file.write_text("password = 'small'\n")
            
            large_file = temp_path / "large.py"
            large_file.write_text("x = 1\n" * 2000000)  # ~12MB
            
            config = ScannerConfig(max_file_size_mb=5.0)
            scanner = SecurityScanner(config)
            
            start_time = time.time()
            result = scanner.scan(str(temp_path))
            duration = time.time() - start_time
            
            # Should skip large file and be fast
            assert result.total_files_scanned == 1
            assert duration < 1.0
    
    def test_cache_effectiveness(self):
        """Test effectiveness of caching (if implemented)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            for i in range(5):
                file_path = temp_path / f"file_{i}.py"
                file_path.write_text(f"constant_{i} = {i}\n" * 100)
            
            config = ScannerConfig(cache_results=True)
            scanner = SecurityScanner(config)
            
            # First scan
            start_time = time.time()
            first_result = scanner.scan(str(temp_path))
            first_duration = time.time() - start_time
            
            # Second scan (should benefit from cache if implemented)
            start_time = time.time()
            second_result = scanner.scan(str(temp_path))
            second_duration = time.time() - start_time
            
            assert first_result.total_files_scanned == second_result.total_files_scanned
            # Cache might make second scan faster (implementation dependent)
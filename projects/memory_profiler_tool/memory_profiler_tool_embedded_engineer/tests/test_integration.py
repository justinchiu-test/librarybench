"""Integration tests for the memory profiler tool."""

import pytest
import tempfile
from pathlib import Path
from src.micro_tracker import MicroTracker
from src.static_analyzer import StaticAnalyzer
from src.fragmentation import FragmentationAnalyzer
from src.optimizer import MemoryOptimizer
from src.cross_platform import CrossPlatformPredictor, Architecture


class TestIntegration:
    """Integration tests combining multiple modules."""
    
    def test_full_workflow(self):
        """Test complete workflow from analysis to optimization."""
        # Sample code to analyze
        source_code = """
def process_data(data_size):
    # Inefficient implementation
    result = ""
    for i in range(data_size):
        result += str(i)
    
    large_list = [i**2 for i in range(data_size)]
    return result, large_list

class DataProcessor:
    def __init__(self):
        self.cache = {}
        self.buffer = []
        
    def process(self, items):
        for item in items:
            self.buffer.append(item * 2)
        return self.buffer
"""
        
        # Step 1: Static analysis
        static_analyzer = StaticAnalyzer(device_memory_limit=100000)
        static_report = static_analyzer.analyze_source(source_code)
        
        assert len(static_report.code_paths) > 0
        assert len(static_report.recommendations) > 0
        
        # Step 2: Optimization recommendations
        optimizer = MemoryOptimizer()
        opt_report = optimizer.analyze_source(source_code)
        
        assert len(opt_report.suggestions) > 0
        assert opt_report.total_potential_savings > 0
        
        # Step 3: Cross-platform prediction
        predictor = CrossPlatformPredictor()
        allocations = [("buffer", 1000), ("cache", 2000)]
        platform_report = predictor.predict_memory(
            allocations, 
            [Architecture.ARM32, Architecture.ESP32]
        )
        
        assert len(platform_report.predictions) == 2
        
    def test_tracking_and_analysis_correlation(self):
        """Test correlation between runtime tracking and static analysis."""
        # Code to test
        test_code = """
def allocate_memory():
    data = [i for i in range(100)]
    return data
"""
        
        # Static analysis
        analyzer = StaticAnalyzer()
        static_report = analyzer.analyze_source(test_code)
        
        # Runtime tracking
        tracker = MicroTracker()
        
        # Create the function
        namespace = {}
        exec(test_code, namespace)
        allocate_memory = namespace['allocate_memory']
        
        with tracker:
            result = allocate_memory()
            
        runtime_stats = tracker.get_stats()
        
        # Both should detect allocations
        assert len(static_report.code_paths) > 0
        assert runtime_stats.total_size > 0
        
    def test_fragmentation_with_real_patterns(self):
        """Test fragmentation with realistic allocation patterns."""
        # Simulate a real application pattern
        analyzer = FragmentationAnalyzer(memory_size=50000)
        
        # Phase 1: Initial allocations
        session_data = []
        for i in range(10):
            addr = analyzer.allocate(1000, f"session_{i}")
            session_data.append(addr)
            
        # Phase 2: Request handling (variable sizes)
        request_data = []
        for i in range(20):
            size = 100 + (i * 50)
            addr = analyzer.allocate(size, f"request_{i}")
            request_data.append(addr)
            
        # Phase 3: Cleanup old sessions
        for i in range(0, 10, 2):
            analyzer.free(session_data[i])
            
        # Phase 4: New allocations in gaps
        for i in range(5):
            addr = analyzer.allocate(800, f"new_session_{i}")
            
        # Analyze fragmentation
        metrics = analyzer.calculate_metrics()
        suggestions = analyzer.suggest_defragmentation_strategies()
        
        assert metrics.fragmentation_percentage > 0
        assert len(suggestions) > 0
        
    def test_optimization_verification(self):
        """Test that optimizations actually reduce memory usage."""
        # Original inefficient code
        original_code = """
def inefficient():
    # String concatenation in loop
    result = ""
    for i in range(1000):
        result += str(i)
    
    # Large list that could be generator
    squares = [x**2 for x in range(10000)]
    total = sum(squares)
    
    return result, total
"""
        
        # Optimized version
        optimized_code = """
def efficient():
    # Using join
    result = ''.join(str(i) for i in range(1000))
    
    # Using generator
    squares = (x**2 for x in range(10000))
    total = sum(squares)
    
    return result, total
"""
        
        # Analyze both versions
        analyzer = StaticAnalyzer()
        original_report = analyzer.analyze_source(original_code)
        optimized_report = analyzer.analyze_source(optimized_code)
        
        # Optimized should use less memory
        assert optimized_report.total_estimate.max_bytes < original_report.total_estimate.max_bytes
        
    def test_platform_specific_optimization(self):
        """Test platform-specific optimization recommendations."""
        code = """
class SensorData:
    def __init__(self):
        self.readings = []
        self.timestamps = []
        self.calibration = {}
        
    def add_reading(self, value, timestamp):
        self.readings.append(value)
        self.timestamps.append(timestamp)
"""
        
        # Analyze for different platforms
        predictor = CrossPlatformPredictor()
        optimizer = MemoryOptimizer()
        
        # Get general optimizations
        opt_report = optimizer.analyze_source(code)
        
        # Predict for constrained platform
        allocations = [("SensorData", 500)]
        platform_report = predictor.predict_memory(allocations, [Architecture.AVR])
        
        # Should have platform-specific warnings
        avr_prediction = platform_report.predictions[Architecture.AVR]
        assert len(avr_prediction.warnings) > 0 or len(platform_report.optimization_suggestions) > 0
        
    def test_memory_leak_detection_workflow(self):
        """Test workflow for detecting memory leaks."""
        tracker = MicroTracker()
        
        # Simulate a memory leak
        leaked_objects = []
        
        with tracker:
            for i in range(10):
                # Objects that aren't released
                leaked_objects.append([0] * 100)
                
            initial_count = len(tracker.get_live_objects())
            
            # Clear some references
            for i in range(5):
                leaked_objects[i] = None
                
            # Track that we still have allocations
            final_count = len(tracker.get_live_objects())
            
        # Should have tracked objects
        assert initial_count > 0
        assert tracker.get_stats().total_count > 0
        
    def test_comprehensive_reporting(self):
        """Test generation of comprehensive memory report."""
        # Sample application code
        app_code = """
import collections

class Application:
    def __init__(self):
        self.users = {}
        self.cache = collections.defaultdict(list)
        self.buffer = bytearray(1024)
        
    def add_user(self, user_id, data):
        self.users[user_id] = data
        self.cache[user_id].append(data)
        
    def process_batch(self, items):
        results = []
        for item in items:
            processed = self._process_item(item)
            results.append(processed)
        return results
        
    def _process_item(self, item):
        # Simulate processing
        temp_buffer = [0] * len(item)
        return sum(temp_buffer)
"""
        
        # Comprehensive analysis
        static_analyzer = StaticAnalyzer()
        optimizer = MemoryOptimizer()
        predictor = CrossPlatformPredictor()
        
        # Static analysis
        static_report = static_analyzer.analyze_source(app_code)
        
        # Optimization analysis
        opt_report = optimizer.analyze_source(app_code)
        
        # Cross-platform prediction
        estimated_allocations = [
            ("Application", 1000),
            ("users_dict", 5000),
            ("cache", 10000),
            ("buffer", 1024)
        ]
        
        platform_report = predictor.predict_memory(
            estimated_allocations,
            [Architecture.ARM32, Architecture.ESP32, Architecture.STM32]
        )
        
        # Verify comprehensive results
        assert static_report.total_estimate.max_bytes > 0
        assert len(opt_report.suggestions) > 0
        assert len(platform_report.predictions) == 3
        
        # Check for specific recommendations
        all_recommendations = (
            static_report.recommendations + 
            opt_report.implementation_plan +
            platform_report.optimization_suggestions
        )
        
        assert len(all_recommendations) > 0
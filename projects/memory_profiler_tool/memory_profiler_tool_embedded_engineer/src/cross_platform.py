"""Cross-compilation memory prediction for target platforms."""

import sys
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class Architecture(Enum):
    """Target architectures."""
    ARM32 = "arm32"
    ARM64 = "arm64" 
    X86 = "x86"
    X86_64 = "x86_64"
    MIPS = "mips"
    RISCV32 = "riscv32"
    RISCV64 = "riscv64"
    AVR = "avr"  # Arduino
    ESP32 = "esp32"
    STM32 = "stm32"


@dataclass
class PlatformProfile:
    """Platform-specific memory characteristics."""
    architecture: Architecture
    word_size: int  # bytes
    pointer_size: int  # bytes
    alignment: int  # bytes
    page_size: int  # bytes
    overhead_factor: float  # Platform-specific overhead multiplier
    type_sizes: Dict[str, int]  # Type-specific sizes
    stack_frame_overhead: int  # bytes
    heap_allocation_overhead: int  # bytes per allocation
    

@dataclass
class MemoryPrediction:
    """Memory usage prediction for a target platform."""
    platform: Architecture
    base_memory: int
    runtime_memory: int
    peak_memory: int
    stack_usage: int
    heap_usage: int
    confidence: float  # 0.0 to 1.0
    warnings: List[str]
    

@dataclass
class CrossPlatformReport:
    """Cross-platform memory analysis report."""
    predictions: Dict[Architecture, MemoryPrediction]
    alignment_issues: List[Tuple[str, int]]  # (description, waste_bytes)
    portability_issues: List[str]
    optimization_suggestions: List[str]
    validation_results: Dict[Architecture, bool]


class CrossPlatformPredictor:
    """Predict memory usage across different embedded platforms."""
    
    # Platform profiles with realistic embedded system characteristics
    PLATFORM_PROFILES = {
        Architecture.ARM32: PlatformProfile(
            architecture=Architecture.ARM32,
            word_size=4,
            pointer_size=4,
            alignment=4,
            page_size=4096,
            overhead_factor=1.1,
            type_sizes={'int': 4, 'float': 4, 'double': 8, 'char': 1, 'bool': 1},
            stack_frame_overhead=8,
            heap_allocation_overhead=8
        ),
        Architecture.ARM64: PlatformProfile(
            architecture=Architecture.ARM64,
            word_size=8,
            pointer_size=8,
            alignment=8,
            page_size=4096,
            overhead_factor=1.15,
            type_sizes={'int': 4, 'float': 4, 'double': 8, 'char': 1, 'bool': 1},
            stack_frame_overhead=16,
            heap_allocation_overhead=16
        ),
        Architecture.X86: PlatformProfile(
            architecture=Architecture.X86,
            word_size=4,
            pointer_size=4,
            alignment=4,
            page_size=4096,
            overhead_factor=1.2,
            type_sizes={'int': 4, 'float': 4, 'double': 8, 'char': 1, 'bool': 1},
            stack_frame_overhead=8,
            heap_allocation_overhead=12
        ),
        Architecture.X86_64: PlatformProfile(
            architecture=Architecture.X86_64,
            word_size=8,
            pointer_size=8,
            alignment=8,
            page_size=4096,
            overhead_factor=1.2,
            type_sizes={'int': 4, 'float': 4, 'double': 8, 'char': 1, 'bool': 1},
            stack_frame_overhead=16,
            heap_allocation_overhead=16
        ),
        Architecture.ESP32: PlatformProfile(
            architecture=Architecture.ESP32,
            word_size=4,
            pointer_size=4,
            alignment=4,
            page_size=256,
            overhead_factor=1.3,  # Higher overhead on microcontrollers
            type_sizes={'int': 4, 'float': 4, 'double': 8, 'char': 1, 'bool': 1},
            stack_frame_overhead=16,
            heap_allocation_overhead=20
        ),
        Architecture.STM32: PlatformProfile(
            architecture=Architecture.STM32,
            word_size=4,
            pointer_size=4,
            alignment=4,
            page_size=256,
            overhead_factor=1.25,
            type_sizes={'int': 4, 'float': 4, 'double': 8, 'char': 1, 'bool': 1},
            stack_frame_overhead=12,
            heap_allocation_overhead=16
        ),
        Architecture.AVR: PlatformProfile(
            architecture=Architecture.AVR,
            word_size=2,
            pointer_size=2,
            alignment=2,
            page_size=128,
            overhead_factor=1.4,  # Very constrained platform
            type_sizes={'int': 2, 'float': 4, 'double': 4, 'char': 1, 'bool': 1},
            stack_frame_overhead=4,
            heap_allocation_overhead=6
        ),
    }
    
    def __init__(self):
        """Initialize the cross-platform predictor."""
        self.host_profile = self._detect_host_platform()
        
    def _detect_host_platform(self) -> PlatformProfile:
        """Detect the host platform characteristics."""
        pointer_size = struct.calcsize("P")
        
        if sys.maxsize > 2**32:
            if sys.platform.startswith('linux'):
                return self.PLATFORM_PROFILES[Architecture.X86_64]
            else:
                return self.PLATFORM_PROFILES[Architecture.X86_64]
        else:
            return self.PLATFORM_PROFILES[Architecture.X86]
            
    def predict_memory(self, 
                      allocations: List[Tuple[str, int]],
                      target_platforms: List[Architecture]) -> CrossPlatformReport:
        """Predict memory usage for target platforms.
        
        Args:
            allocations: List of (type, size) allocations on host
            target_platforms: List of target architectures
            
        Returns:
            Cross-platform memory report
        """
        predictions = {}
        alignment_issues = []
        portability_issues = []
        
        for platform in target_platforms:
            if platform not in self.PLATFORM_PROFILES:
                portability_issues.append(f"Unknown platform: {platform}")
                continue
                
            profile = self.PLATFORM_PROFILES[platform]
            prediction = self._predict_for_platform(allocations, profile)
            predictions[platform] = prediction
            
            # Check alignment issues
            alignment_waste = self._check_alignment_waste(allocations, profile)
            if alignment_waste:
                alignment_issues.extend(alignment_waste)
                
        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(predictions)
        
        # Validate predictions
        validation_results = self._validate_predictions(predictions)
        
        return CrossPlatformReport(
            predictions=predictions,
            alignment_issues=sorted(alignment_issues, key=lambda x: x[1], reverse=True),
            portability_issues=portability_issues,
            optimization_suggestions=suggestions,
            validation_results=validation_results
        )
        
    def _predict_for_platform(self, 
                             allocations: List[Tuple[str, int]],
                             profile: PlatformProfile) -> MemoryPrediction:
        """Predict memory usage for a specific platform."""
        base_memory = 0
        heap_usage = 0
        warnings = []
        
        for obj_type, host_size in allocations:
            # Translate size based on platform differences
            target_size = self._translate_size(obj_type, host_size, profile)
            
            # Add alignment padding
            aligned_size = self._align_size(target_size, profile.alignment)
            
            # Add allocation overhead
            total_size = aligned_size + profile.heap_allocation_overhead
            
            heap_usage += total_size
            
        # Calculate runtime memory (with overhead)
        runtime_memory = int(heap_usage * profile.overhead_factor)
        
        # Estimate stack usage (simplified)
        stack_usage = 4096  # Base stack
        
        # Peak memory estimate
        peak_memory = runtime_memory + stack_usage
        
        # Platform-specific warnings
        if profile.architecture == Architecture.AVR and peak_memory > 2048:
            warnings.append("Memory usage exceeds typical AVR RAM size (2KB)")
        elif profile.architecture == Architecture.ESP32 and peak_memory > 320 * 1024:
            warnings.append("Memory usage high for ESP32 (>320KB)")
            
        return MemoryPrediction(
            platform=profile.architecture,
            base_memory=base_memory,
            runtime_memory=runtime_memory,
            peak_memory=peak_memory,
            stack_usage=stack_usage,
            heap_usage=heap_usage,
            confidence=0.8,
            warnings=warnings
        )
        
    def _translate_size(self, obj_type: str, host_size: int, 
                       target_profile: PlatformProfile) -> int:
        """Translate object size from host to target platform."""
        # Simple heuristic based on pointer size differences
        host_pointer_size = self.host_profile.pointer_size
        target_pointer_size = target_profile.pointer_size
        
        if 'list' in obj_type or 'dict' in obj_type:
            # Collections have pointers that need scaling
            pointer_count = host_size // (8 * host_pointer_size)  # Estimate
            base_size = host_size - (pointer_count * host_pointer_size)
            return base_size + (pointer_count * target_pointer_size)
        else:
            # Simple scaling for other types
            scale_factor = target_profile.word_size / self.host_profile.word_size
            return int(host_size * scale_factor)
            
    def _align_size(self, size: int, alignment: int) -> int:
        """Align size to platform requirements."""
        if size % alignment == 0:
            return size
        return size + (alignment - (size % alignment))
        
    def _check_alignment_waste(self, 
                              allocations: List[Tuple[str, int]],
                              profile: PlatformProfile) -> List[Tuple[str, int]]:
        """Check for memory waste due to alignment."""
        waste_list = []
        
        for obj_type, size in allocations:
            aligned_size = self._align_size(size, profile.alignment)
            waste = aligned_size - size
            
            if waste > 0:
                waste_list.append((f"{obj_type} alignment padding", waste))
                
        return waste_list
        
    def _generate_optimization_suggestions(self, 
                                         predictions: Dict[Architecture, MemoryPrediction]) -> List[str]:
        """Generate platform-specific optimization suggestions."""
        suggestions = []
        
        # Check for high memory usage on constrained platforms
        for arch, pred in predictions.items():
            if arch in [Architecture.AVR, Architecture.ESP32, Architecture.STM32]:
                if pred.peak_memory > 64 * 1024:  # 64KB
                    suggestions.append(
                        f"Consider memory optimization for {arch.value}: "
                        f"peak usage is {pred.peak_memory // 1024}KB"
                    )
                    
        # Alignment optimization
        total_platforms = len(predictions)
        if total_platforms > 1:
            # Find common alignment
            alignments = [self.PLATFORM_PROFILES[arch].alignment 
                         for arch in predictions.keys()
                         if arch in self.PLATFORM_PROFILES]
            
            if alignments:
                max_alignment = max(alignments)
                suggestions.append(
                    f"Use {max_alignment}-byte alignment for cross-platform compatibility"
                )
                
        return suggestions
        
    def _validate_predictions(self, 
                            predictions: Dict[Architecture, MemoryPrediction]) -> Dict[Architecture, bool]:
        """Validate predictions against known constraints."""
        validation = {}
        
        # Platform memory limits
        MEMORY_LIMITS = {
            Architecture.AVR: 2 * 1024,  # 2KB typical
            Architecture.ESP32: 512 * 1024,  # 512KB
            Architecture.STM32: 128 * 1024,  # 128KB typical
            Architecture.ARM32: 256 * 1024 * 1024,  # 256MB
            Architecture.ARM64: 1024 * 1024 * 1024,  # 1GB
        }
        
        for arch, pred in predictions.items():
            limit = MEMORY_LIMITS.get(arch, float('inf'))
            validation[arch] = pred.peak_memory <= limit
            
        return validation
        
    def model_allocation_pattern(self, 
                                pattern: str,
                                count: int,
                                size: int) -> List[Tuple[str, int]]:
        """Model common allocation patterns.
        
        Args:
            pattern: Pattern type ('sequential', 'random', 'burst')
            count: Number of allocations
            size: Size of each allocation
            
        Returns:
            List of allocations
        """
        allocations = []
        
        if pattern == 'sequential':
            for i in range(count):
                allocations.append((f"object_{i}", size))
        elif pattern == 'random':
            import random
            for i in range(count):
                random_size = random.randint(size // 2, size * 2)
                allocations.append((f"random_{i}", random_size))
        elif pattern == 'burst':
            # Simulate burst allocations
            for burst in range(count // 10):
                for i in range(10):
                    allocations.append((f"burst_{burst}_{i}", size))
                    
        return allocations
        
    def compare_platforms(self, 
                         allocations: List[Tuple[str, int]]) -> Dict[str, Any]:
        """Compare memory usage across all supported platforms.
        
        Args:
            allocations: List of allocations
            
        Returns:
            Comparison results
        """
        all_platforms = list(self.PLATFORM_PROFILES.keys())
        report = self.predict_memory(allocations, all_platforms)
        
        comparison = {
            'most_efficient': None,
            'least_efficient': None,
            'platform_rankings': [],
            'memory_range': (float('inf'), 0)
        }
        
        # Rank platforms by memory usage
        rankings = []
        min_memory = float('inf')
        max_memory = 0
        
        for arch, pred in report.predictions.items():
            rankings.append((arch, pred.peak_memory))
            min_memory = min(min_memory, pred.peak_memory)
            max_memory = max(max_memory, pred.peak_memory)
            
        rankings.sort(key=lambda x: x[1])
        
        if rankings:
            comparison['most_efficient'] = rankings[0][0]
            comparison['least_efficient'] = rankings[-1][0]
            comparison['platform_rankings'] = rankings
            comparison['memory_range'] = (min_memory, max_memory)
            
        return comparison
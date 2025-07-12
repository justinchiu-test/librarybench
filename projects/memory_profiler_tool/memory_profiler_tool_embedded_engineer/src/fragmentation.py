"""Memory fragmentation visualization and metrics."""

import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import math


@dataclass
class MemoryBlock:
    """Represents a memory block."""
    address: int
    size: int
    is_free: bool
    object_type: Optional[str] = None
    
    @property
    def end_address(self) -> int:
        """Get end address of block."""
        return self.address + self.size


@dataclass
class FragmentationMetrics:
    """Memory fragmentation metrics."""
    total_memory: int
    used_memory: int
    free_memory: int
    fragmentation_percentage: float
    largest_free_block: int
    free_block_count: int
    average_free_block_size: float
    memory_efficiency: float  # 0.0 to 1.0
    
    
@dataclass 
class FragmentationReport:
    """Complete fragmentation analysis report."""
    metrics: FragmentationMetrics
    memory_map: List[MemoryBlock]
    fragmentation_hotspots: List[Tuple[str, float]]  # (location, fragmentation_score)
    defragmentation_suggestions: List[str]
    visualization: str


class FragmentationAnalyzer:
    """Analyze and visualize memory fragmentation."""
    
    def __init__(self, memory_size: int = 1024 * 1024):  # 1MB default
        """Initialize fragmentation analyzer.
        
        Args:
            memory_size: Total memory size to simulate
        """
        self.memory_size = memory_size
        self.memory_blocks: List[MemoryBlock] = []
        self.allocation_history: List[Tuple[int, int, str]] = []  # (address, size, type)
        self._init_memory()
        
    def _init_memory(self) -> None:
        """Initialize memory as one large free block."""
        self.memory_blocks = [
            MemoryBlock(address=0, size=self.memory_size, is_free=True)
        ]
        
    def allocate(self, size: int, object_type: str = "unknown") -> Optional[int]:
        """Simulate memory allocation.
        
        Args:
            size: Size to allocate
            object_type: Type of object being allocated
            
        Returns:
            Address of allocated block or None if failed
        """
        # Handle zero-size allocation
        if size == 0:
            # Return a valid address but don't actually allocate
            if self.memory_blocks and self.memory_blocks[0].is_free:
                return self.memory_blocks[0].address
            return 0
            
        # Find first-fit free block
        for i, block in enumerate(self.memory_blocks):
            if block.is_free and block.size >= size:
                # Split block if necessary
                if block.size > size:
                    new_free_block = MemoryBlock(
                        address=block.address + size,
                        size=block.size - size,
                        is_free=True
                    )
                    self.memory_blocks.insert(i + 1, new_free_block)
                    
                # Mark block as used
                block.size = size
                block.is_free = False
                block.object_type = object_type
                
                self.allocation_history.append((block.address, size, object_type))
                return block.address
                
        return None
        
    def free(self, address: int) -> bool:
        """Free memory at address.
        
        Args:
            address: Address to free
            
        Returns:
            True if successful, False otherwise
        """
        for i, block in enumerate(self.memory_blocks):
            if block.address == address and not block.is_free:
                block.is_free = True
                block.object_type = None
                
                # Coalesce adjacent free blocks
                self._coalesce_free_blocks()
                return True
                
        return False
        
    def _coalesce_free_blocks(self) -> None:
        """Merge adjacent free blocks."""
        i = 0
        while i < len(self.memory_blocks) - 1:
            current = self.memory_blocks[i]
            next_block = self.memory_blocks[i + 1]
            
            if current.is_free and next_block.is_free:
                # Merge blocks
                current.size += next_block.size
                self.memory_blocks.pop(i + 1)
            else:
                i += 1
                
    def calculate_metrics(self) -> FragmentationMetrics:
        """Calculate fragmentation metrics.
        
        Returns:
            Fragmentation metrics
        """
        free_blocks = [b for b in self.memory_blocks if b.is_free]
        used_blocks = [b for b in self.memory_blocks if not b.is_free]
        
        total_free = sum(b.size for b in free_blocks)
        total_used = sum(b.size for b in used_blocks)
        
        # Calculate fragmentation percentage
        if free_blocks and total_free > 0:
            largest_free = max(b.size for b in free_blocks)
            fragmentation = 1.0 - (largest_free / total_free)
        else:
            fragmentation = 0.0
            largest_free = 0
            
        # Memory efficiency
        efficiency = total_used / self.memory_size if self.memory_size > 0 else 0.0
        
        return FragmentationMetrics(
            total_memory=self.memory_size,
            used_memory=total_used,
            free_memory=total_free,
            fragmentation_percentage=fragmentation * 100,
            largest_free_block=largest_free,
            free_block_count=len(free_blocks),
            average_free_block_size=total_free / len(free_blocks) if free_blocks else 0,
            memory_efficiency=efficiency
        )
        
    def visualize_memory(self, width: int = 80, height: int = 20) -> str:
        """Create text-based memory visualization.
        
        Args:
            width: Width of visualization in characters
            height: Height of visualization in lines
            
        Returns:
            ASCII art memory map
        """
        if not self.memory_blocks:
            return "No memory blocks"
            
        lines = []
        lines.append("Memory Map:")
        lines.append("=" * width)
        
        # Create memory bar
        bar = []
        for block in self.memory_blocks:
            block_width = max(1, int((block.size / self.memory_size) * width))
            char = '█' if not block.is_free else '░'
            bar.extend([char] * block_width)
            
        # Ensure bar is exactly width characters
        bar = bar[:width]
        while len(bar) < width:
            bar.append(' ')
            
        # Split into multiple lines if needed
        for i in range(0, len(bar), width):
            lines.append(''.join(bar[i:i+width]))
            
        lines.append("=" * width)
        
        # Add legend
        lines.append("Legend: █=Used ░=Free")
        
        # Add block details
        lines.append("\nMemory Blocks:")
        for block in self.memory_blocks[:10]:  # Show first 10 blocks
            status = "FREE" if block.is_free else f"USED ({block.object_type})"
            lines.append(f"  0x{block.address:08X}-0x{block.end_address:08X} "
                        f"({block.size:8d} bytes) {status}")
                        
        if len(self.memory_blocks) > 10:
            lines.append(f"  ... and {len(self.memory_blocks) - 10} more blocks")
            
        return '\n'.join(lines)
        
    def identify_fragmentation_hotspots(self) -> List[Tuple[str, float]]:
        """Identify code locations causing fragmentation.
        
        Returns:
            List of (location, fragmentation_score) tuples
        """
        # Analyze allocation patterns
        type_patterns: Dict[str, List[int]] = defaultdict(list)
        
        for addr, size, obj_type in self.allocation_history:
            type_patterns[obj_type].append(size)
            
        hotspots = []
        
        for obj_type, sizes in type_patterns.items():
            if len(sizes) < 2:
                continue
                
            # Calculate size variance
            avg_size = sum(sizes) / len(sizes)
            variance = sum((s - avg_size) ** 2 for s in sizes) / len(sizes)
            std_dev = math.sqrt(variance)
            
            # High variance in allocation sizes causes fragmentation
            fragmentation_score = std_dev / avg_size if avg_size > 0 else 0
            
            if fragmentation_score > 0.5:
                hotspots.append((f"Type: {obj_type}", fragmentation_score))
                
        return sorted(hotspots, key=lambda x: x[1], reverse=True)
        
    def suggest_defragmentation_strategies(self) -> List[str]:
        """Suggest strategies to reduce fragmentation.
        
        Returns:
            List of defragmentation suggestions
        """
        suggestions = []
        metrics = self.calculate_metrics()
        
        if metrics.fragmentation_percentage > 30:
            suggestions.append("High fragmentation detected. Consider:")
            
            # Analyze allocation patterns
            sizes = [b.size for b in self.memory_blocks if not b.is_free]
            if sizes:
                avg_size = sum(sizes) / len(sizes)
                
                # Check for mixed allocation sizes
                small_allocs = sum(1 for s in sizes if s < avg_size / 2)
                large_allocs = sum(1 for s in sizes if s > avg_size * 2)
                
                if small_allocs > 0 and large_allocs > 0:
                    suggestions.append(
                        "- Segregate small and large allocations into separate pools"
                    )
                    
            # Check for many small free blocks
            if metrics.free_block_count > 10 and metrics.average_free_block_size < 100:
                suggestions.append(
                    "- Implement memory pooling for frequently allocated objects"
                )
                
            # Check allocation frequency
            if len(self.allocation_history) > 100:
                suggestions.append(
                    "- Consider using object recycling to reduce allocation frequency"
                )
                
            suggestions.append(
                "- Use fixed-size allocation blocks for similar objects"
            )
            
        if metrics.memory_efficiency < 0.7:
            suggestions.append(
                "Low memory utilization. Review allocation patterns and sizes."
            )
            
        return suggestions
        
    def analyze_allocation_pattern(self, 
                                 allocations: List[Tuple[int, str]]) -> FragmentationReport:
        """Analyze a sequence of allocations for fragmentation.
        
        Args:
            allocations: List of (size, type) tuples
            
        Returns:
            Fragmentation analysis report
        """
        # Reset memory
        self._init_memory()
        self.allocation_history.clear()
        
        # Perform allocations
        allocated_addresses = []
        for size, obj_type in allocations:
            addr = self.allocate(size, obj_type)
            if addr is not None:
                allocated_addresses.append(addr)
                
        # Free some allocations to create fragmentation
        for i, addr in enumerate(allocated_addresses):
            if i % 2 == 0:  # Free every other allocation
                self.free(addr)
                
        # Generate report
        metrics = self.calculate_metrics()
        visualization = self.visualize_memory()
        hotspots = self.identify_fragmentation_hotspots()
        suggestions = self.suggest_defragmentation_strategies()
        
        return FragmentationReport(
            metrics=metrics,
            memory_map=self.memory_blocks.copy(),
            fragmentation_hotspots=hotspots,
            defragmentation_suggestions=suggestions,
            visualization=visualization
        )
        
    def export_memory_map(self) -> List[Dict[str, any]]:
        """Export memory map as JSON-serializable structure.
        
        Returns:
            List of memory block dictionaries
        """
        return [
            {
                'address': block.address,
                'size': block.size,
                'is_free': block.is_free,
                'object_type': block.object_type,
                'end_address': block.end_address
            }
            for block in self.memory_blocks
        ]
"""Tests for the asset memory manager module."""

import time
import pytest
from pymemtrace.asset_manager import (
    AssetMemoryManager, AssetType, AssetState, AssetInfo
)


class TestAssetMemoryManager:
    """Test suite for AssetMemoryManager."""
    
    def test_initialization(self):
        """Test manager initialization."""
        manager = AssetMemoryManager()
        assert len(manager.assets) == 0
        assert len(manager.orphaned_assets) == 0
    
    def test_register_asset(self):
        """Test asset registration."""
        manager = AssetMemoryManager()
        
        # Create a test asset
        test_texture = b"texture_data" * 1000
        
        manager.register_asset(
            asset_id="texture_001",
            asset_type=AssetType.TEXTURE,
            asset_object=test_texture,
            metadata={"width": 1024, "height": 1024}
        )
        
        assert "texture_001" in manager.assets
        asset_info = manager.get_asset_info("texture_001")
        assert asset_info.asset_type == AssetType.TEXTURE
        assert asset_info.state == AssetState.LOADED
        assert asset_info.reference_count == 1
        assert asset_info.metadata["width"] == 1024
    
    def test_asset_lifecycle_states(self):
        """Test asset state transitions."""
        manager = AssetMemoryManager()
        test_asset = {"data": "test"}
        
        manager.register_asset("asset_001", AssetType.MODEL, test_asset)
        
        # Test state transitions
        manager.update_asset_state("asset_001", AssetState.IN_USE)
        assert manager.get_asset_info("asset_001").state == AssetState.IN_USE
        
        manager.update_asset_state("asset_001", AssetState.CACHED)
        assert manager.get_asset_info("asset_001").state == AssetState.CACHED
    
    def test_reference_counting(self):
        """Test asset reference counting."""
        manager = AssetMemoryManager()
        test_asset = [1, 2, 3]
        
        manager.register_asset("asset_001", AssetType.SOUND, test_asset)
        
        # Add references
        manager.add_reference("asset_001", "player_1")
        manager.add_reference("asset_001", "player_2")
        
        asset = manager.get_asset_info("asset_001")
        assert asset.reference_count == 3  # Initial + 2 added
        
        # Remove references
        manager.remove_reference("asset_001", "player_1")
        assert manager.get_asset_info("asset_001").reference_count == 2
    
    def test_dependency_tracking(self):
        """Test asset dependency management."""
        manager = AssetMemoryManager()
        
        # Register assets
        manager.register_asset("shader_001", AssetType.SHADER, {})
        manager.register_asset("material_001", AssetType.OTHER, {})
        
        # Add dependency
        manager.add_dependency("material_001", "shader_001")
        
        material = manager.get_asset_info("material_001")
        assert "shader_001" in material.dependencies
    
    def test_memory_by_type(self):
        """Test memory calculation by asset type."""
        manager = AssetMemoryManager()
        
        # Register different asset types
        manager.register_asset("tex_1", AssetType.TEXTURE, b"x" * 1000)
        manager.register_asset("tex_2", AssetType.TEXTURE, b"x" * 2000)
        manager.register_asset("sound_1", AssetType.SOUND, b"x" * 500)
        
        memory_by_type = manager.get_total_memory_by_type()
        
        assert AssetType.TEXTURE in memory_by_type
        assert AssetType.SOUND in memory_by_type
        assert memory_by_type[AssetType.TEXTURE] > memory_by_type[AssetType.SOUND]
    
    def test_memory_heatmap(self):
        """Test memory heatmap generation."""
        manager = AssetMemoryManager()
        
        # Register assets with different sizes
        manager.register_asset("large_texture", AssetType.TEXTURE, b"x" * 10000)
        manager.register_asset("small_sound", AssetType.SOUND, b"x" * 100)
        manager.register_asset("medium_model", AssetType.MODEL, b"x" * 5000)
        
        heatmap = manager.get_memory_heatmap(top_n=2)
        
        assert heatmap.total_memory > 0
        assert len(heatmap.hotspots) == 2
        assert heatmap.hotspots[0][0] == "large_texture"
    
    def test_unused_assets_detection(self):
        """Test detection of unused assets."""
        manager = AssetMemoryManager()
        
        # Register an asset
        manager.register_asset("old_asset", AssetType.TEXTURE, {})
        
        # Simulate time passing
        time.sleep(0.1)
        
        # Register and use a new asset
        manager.register_asset("new_asset", AssetType.TEXTURE, {})
        manager.update_asset_state("new_asset", AssetState.IN_USE)
        
        unused = manager.get_unused_assets(threshold_seconds=0.05)
        assert "old_asset" in unused
        assert "new_asset" not in unused
    
    def test_memory_leak_detection(self):
        """Test detection of memory leaks."""
        manager = AssetMemoryManager()
        
        # Create a scenario with orphaned asset
        test_asset = {"data": "leak"}
        manager.register_asset("leak_asset", AssetType.MODEL, test_asset)
        
        # Simulate the asset being deleted but references remaining
        manager.orphaned_assets.add("leak_asset")
        
        leaks = manager.detect_memory_leaks()
        assert "leak_asset" in leaks
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        manager = AssetMemoryManager()
        
        # Create assets with circular dependencies
        manager.register_asset("asset_a", AssetType.OTHER, {})
        manager.register_asset("asset_b", AssetType.OTHER, {})
        manager.register_asset("asset_c", AssetType.OTHER, {})
        
        manager.add_dependency("asset_a", "asset_b")
        manager.add_dependency("asset_b", "asset_c")
        manager.add_dependency("asset_c", "asset_a")  # Circular!
        
        leaks = manager.detect_memory_leaks()
        # All three assets should be detected as having circular deps
        assert any(asset in leaks for asset in ["asset_a", "asset_b", "asset_c"])
    
    def test_lifecycle_stats(self):
        """Test asset lifecycle statistics."""
        manager = AssetMemoryManager()
        
        # Register assets in different states
        manager.register_asset("loaded_1", AssetType.TEXTURE, {})
        manager.register_asset("loaded_2", AssetType.TEXTURE, {})
        
        manager.register_asset("cached_1", AssetType.SOUND, {})
        manager.update_asset_state("cached_1", AssetState.CACHED)
        
        stats = manager.get_asset_lifecycle_stats()
        assert stats[AssetState.LOADED] == 2
        assert stats[AssetState.CACHED] == 1
    
    def test_reference_validation(self):
        """Test reference count validation."""
        manager = AssetMemoryManager()
        
        manager.register_asset("asset_1", AssetType.MODEL, {})
        
        # Add tracked references
        manager.add_reference("asset_1", "ref_1")
        manager.add_reference("asset_1", "ref_2")
        
        # Manually corrupt reference count
        manager.assets["asset_1"].reference_count = 5  # Wrong!
        
        invalid = manager.validate_references()
        assert "asset_1" in invalid
        assert "ref_count_mismatch" in invalid["asset_1"][0]
    
    def test_asset_unloading(self):
        """Test asset unloading."""
        manager = AssetMemoryManager()
        
        manager.register_asset("unload_me", AssetType.TEXTURE, {})
        
        # Can't unload with references
        assert not manager.unload_asset("unload_me")
        
        # Remove all references
        manager.assets["unload_me"].reference_count = 0
        
        # Now can unload
        assert manager.unload_asset("unload_me")
        assert manager.get_asset_info("unload_me").state == AssetState.UNLOADED
    
    def test_dependency_graph(self):
        """Test dependency graph generation."""
        manager = AssetMemoryManager()
        
        # Create asset hierarchy
        manager.register_asset("root", AssetType.LEVEL, {})
        manager.register_asset("child1", AssetType.MODEL, {})
        manager.register_asset("child2", AssetType.TEXTURE, {})
        manager.register_asset("grandchild", AssetType.SHADER, {})
        
        manager.add_dependency("root", "child1")
        manager.add_dependency("root", "child2")
        manager.add_dependency("child1", "grandchild")
        
        graph = manager.get_dependency_graph("root")
        
        assert "root" in graph
        assert "child1" in graph["root"]
        assert "child2" in graph["root"]
        assert "grandchild" in graph["child1"]
    
    def test_total_memory_calculation(self):
        """Test total memory calculation."""
        manager = AssetMemoryManager()
        
        # Register assets in various states
        manager.register_asset("loaded", AssetType.TEXTURE, b"x" * 1000)
        
        manager.register_asset("cached", AssetType.SOUND, b"x" * 500)
        manager.update_asset_state("cached", AssetState.CACHED)
        
        manager.register_asset("unloaded", AssetType.MODEL, b"x" * 2000)
        manager.update_asset_state("unloaded", AssetState.UNLOADED)
        
        # With cached
        total_with_cached = manager.calculate_total_memory(include_cached=True)
        
        # Without cached
        total_without_cached = manager.calculate_total_memory(include_cached=False)
        
        assert total_with_cached > total_without_cached
        assert total_without_cached > 0
    
    def test_clear_orphaned_assets(self):
        """Test clearing orphaned assets."""
        manager = AssetMemoryManager()
        
        # Add orphaned assets
        manager.orphaned_assets.add("orphan_1")
        manager.orphaned_assets.add("orphan_2")
        
        count = manager.clear_orphaned_assets()
        assert count == 2
        assert len(manager.orphaned_assets) == 0
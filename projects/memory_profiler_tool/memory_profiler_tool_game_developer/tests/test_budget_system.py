"""Tests for the memory budget system module."""

import time
import pytest
from unittest.mock import Mock
from pymemtrace.budget_system import (
    MemoryBudgetSystem, MemoryBudget, BudgetViolation,
    BudgetViolationType, EvictionStrategy, EvictableAsset
)


class TestMemoryBudgetSystem:
    """Test suite for MemoryBudgetSystem."""
    
    def test_initialization(self):
        """Test budget system initialization."""
        system = MemoryBudgetSystem()
        assert len(system.budgets) == 0
        assert system._auto_evict_enabled is True
        assert system._eviction_strategy == EvictionStrategy.HYBRID
    
    def test_create_budget(self):
        """Test budget creation."""
        system = MemoryBudgetSystem()
        
        system.create_budget(
            name="graphics",
            max_bytes=1024 * 1024 * 100,  # 100MB
            warning_threshold=0.75,
            critical_threshold=0.90,
            priority=10
        )
        
        assert "graphics" in system.budgets
        budget = system.budgets["graphics"]
        assert budget.max_bytes == 1024 * 1024 * 100
        assert budget.warning_threshold == 0.75
        assert budget.priority == 10
    
    def test_hierarchical_budgets(self):
        """Test hierarchical budget system."""
        system = MemoryBudgetSystem()
        
        # Create parent budget
        system.create_budget("total", max_bytes=1000)
        
        # Create child budgets
        system.create_budget("graphics", max_bytes=500, parent="total")
        system.create_budget("audio", max_bytes=300, parent="total")
        
        # Register asset in child budget
        system.register_asset("texture_1", "graphics", size=100)
        
        # Both child and parent usage should update
        assert system.usage["graphics"] == 100
        assert system.usage["total"] == 100
    
    def test_asset_registration(self):
        """Test asset registration with budget."""
        system = MemoryBudgetSystem()
        system.create_budget("assets", max_bytes=1000)
        
        system.register_asset(
            asset_id="model_001",
            budget_name="assets",
            size=200,
            priority=5,
            subsystem="models"
        )
        
        assert "model_001" in system.assets
        assert system.asset_to_budget["model_001"] == "assets"
        assert system.usage["assets"] == 200
    
    def test_budget_violations(self):
        """Test budget violation detection."""
        system = MemoryBudgetSystem()
        violations = []
        
        def violation_callback(violation: BudgetViolation):
            violations.append(violation)
        
        system.add_violation_callback(violation_callback)
        system.create_budget("test", max_bytes=1000, warning_threshold=0.8)
        
        # Add asset that triggers warning
        system.register_asset("asset_1", "test", size=850)
        
        assert len(violations) == 1
        assert violations[0].violation_type == BudgetViolationType.WARNING
        
        # Add more to exceed limit
        system.register_asset("asset_2", "test", size=200)
        
        assert len(violations) == 2
        assert violations[1].violation_type == BudgetViolationType.EXCEEDED
    
    def test_auto_eviction(self):
        """Test automatic asset eviction."""
        system = MemoryBudgetSystem()
        evicted = []
        
        def eviction_callback(asset_id: str, reason: str):
            evicted.append((asset_id, reason))
        
        system.add_eviction_callback(eviction_callback)
        system.create_budget("memory", max_bytes=1000)
        
        # Fill budget
        for i in range(5):
            system.register_asset(f"asset_{i}", "memory", size=200, priority=i)
        
        # This should trigger auto-eviction
        system.register_asset("asset_overflow", "memory", size=200, priority=10)
        
        assert len(evicted) > 0
        assert system.usage["memory"] <= 1000
    
    def test_eviction_strategies(self):
        """Test different eviction strategies."""
        system = MemoryBudgetSystem()
        system.create_budget("test", max_bytes=1000)
        
        # Register assets with different characteristics
        system.register_asset("old_asset", "test", size=100, priority=5)
        time.sleep(0.01)
        system.register_asset("large_asset", "test", size=300, priority=5)
        system.register_asset("low_priority", "test", size=100, priority=1)
        
        # Test LRU strategy
        system.set_eviction_strategy(EvictionStrategy.LRU)
        asset = system.assets["old_asset"]
        score_lru = system._calculate_eviction_score(asset)
        
        # Test SIZE strategy
        system.set_eviction_strategy(EvictionStrategy.SIZE)
        asset = system.assets["large_asset"]
        score_size = system._calculate_eviction_score(asset)
        
        assert score_size == 300  # Size-based score
    
    def test_budget_status(self):
        """Test budget status reporting."""
        system = MemoryBudgetSystem()
        system.create_budget("game", max_bytes=1000)
        
        system.register_asset("asset_1", "game", size=300)
        system.register_asset("asset_2", "game", size=200)
        
        status = system.get_budget_status("game")
        
        assert status["usage"] == 500
        assert status["limit"] == 1000
        assert status["usage_percentage"] == 50.0
        assert status["asset_count"] == 2
        assert not status["is_warning"]
        assert not status["is_exceeded"]
    
    def test_eviction_suggestions(self):
        """Test eviction suggestions."""
        system = MemoryBudgetSystem()
        system.create_budget("limited", max_bytes=1000)
        
        # Register assets
        system.register_asset("small_1", "limited", size=100)
        system.register_asset("large_1", "limited", size=400)
        system.register_asset("small_2", "limited", size=100)
        
        # Suggest evictions to free 300 bytes
        suggestions = system.suggest_evictions("limited", bytes_needed=300)
        
        assert len(suggestions) > 0
        total_suggested = sum(size for _, size in suggestions)
        assert total_suggested >= 300
    
    def test_budget_hierarchy_status(self):
        """Test hierarchical budget status."""
        system = MemoryBudgetSystem()
        
        # Create hierarchy
        system.create_budget("root", max_bytes=2000)
        system.create_budget("child1", max_bytes=1000, parent="root")
        system.create_budget("child2", max_bytes=800, parent="root")
        
        # Add assets
        system.register_asset("a1", "child1", size=500)
        system.register_asset("a2", "child2", size=300)
        
        hierarchy = system.get_hierarchy_status()
        
        assert "root" in hierarchy
        assert "children" in hierarchy["root"]
        assert "child1" in hierarchy["root"]["children"]
        assert hierarchy["root"]["usage"] == 800  # Total from children
    
    def test_budget_analytics(self):
        """Test budget system analytics."""
        system = MemoryBudgetSystem()
        
        # Create budgets
        system.create_budget("b1", max_bytes=1000)
        system.create_budget("b2", max_bytes=2000)
        
        # Add assets
        system.register_asset("a1", "b1", size=900)  # Near limit
        system.register_asset("a2", "b2", size=500)
        
        analytics = system.get_budget_analytics()
        
        assert analytics["total_budgets"] == 2
        assert analytics["total_allocated"] == 3000
        assert analytics["total_used"] == 1400
        assert analytics["budgets_over_warning"] == 1  # b1 is over 80%
        assert analytics["budgets_exceeded"] == 0
    
    def test_disable_auto_eviction(self):
        """Test disabling automatic eviction."""
        system = MemoryBudgetSystem()
        system.enable_auto_eviction(False)
        
        violations = []
        system.add_violation_callback(lambda v: violations.append(v))
        
        system.create_budget("no_evict", max_bytes=100)
        
        # Add assets exceeding budget
        system.register_asset("a1", "no_evict", size=60)
        system.register_asset("a2", "no_evict", size=60)
        
        # Should have violation but no eviction
        assert len(violations) > 0
        assert system.usage["no_evict"] == 120  # Over budget
        assert len(system.assets) == 2  # No assets evicted
    
    def test_asset_usage_update(self):
        """Test updating asset usage statistics."""
        system = MemoryBudgetSystem()
        system.create_budget("tracking", max_bytes=1000)
        
        system.register_asset("tracked", "tracking", size=100)
        
        initial_asset = system.assets["tracked"]
        initial_time = initial_asset.last_used
        initial_count = initial_asset.use_count
        
        time.sleep(0.01)
        system.update_asset_usage("tracked")
        
        updated_asset = system.assets["tracked"]
        assert updated_asset.last_used > initial_time
        assert updated_asset.use_count == initial_count + 1
    
    def test_invalid_budget_registration(self):
        """Test registering asset to non-existent budget."""
        system = MemoryBudgetSystem()
        
        with pytest.raises(ValueError, match="Budget 'nonexistent' does not exist"):
            system.register_asset("asset", "nonexistent", size=100)
    
    def test_eviction_score_calculation(self):
        """Test eviction score calculation for different strategies."""
        system = MemoryBudgetSystem()
        
        # Create an asset for testing
        asset = EvictableAsset(
            asset_id="test",
            size=1000,
            last_used=time.time() - 100,
            use_count=5,
            priority=50,
            age=time.time() - 200,
            subsystem="test"
        )
        
        # Test each strategy
        strategies = [
            EvictionStrategy.LRU,
            EvictionStrategy.LFU,
            EvictionStrategy.PRIORITY,
            EvictionStrategy.SIZE,
            EvictionStrategy.AGE,
            EvictionStrategy.HYBRID
        ]
        
        for strategy in strategies:
            system.set_eviction_strategy(strategy)
            score = system._calculate_eviction_score(asset)
            assert isinstance(score, (int, float))
            assert score >= 0
"""Simple test to check the implementation."""

# Check if all required aliases are defined
methods_to_check = [
    # Graph methods
    "get_root_nodes", "get_root_stages", 
    "get_leaf_nodes", "get_leaf_stages",
    "get_ready_nodes", "get_ready_stages",
    
    # Tracker methods
    "create_graph", "create_dependency_graph",
    "get_graph", "get_dependency_graph",
    "is_ready_to_run", "is_stage_ready",
    "get_ready_jobs", "get_ready_stages",
    "get_blocking_jobs", "get_blocking_stages",
    "update_status", "update_stage_status",
    "validate", "validate_simulation"
]

# Check if all aliases are defined
from common.dependency_tracking.graph import DependencyGraph
from common.dependency_tracking.tracker import DependencyTracker

print("Checking DependencyGraph aliases:")
graph = DependencyGraph("test")
for method in methods_to_check:
    if hasattr(graph, method):
        print(f"  ✅ {method}")
    else:
        print(f"  ❌ {method}")

print("\nChecking DependencyTracker aliases:")
tracker = DependencyTracker()
for method in methods_to_check:
    if hasattr(tracker, method):
        print(f"  ✅ {method}")
    else:
        print(f"  ❌ {method}")

# Check Dependency class aliases
from common.core.models import Dependency

dependency = Dependency(from_id="test-from", to_id="test-to")
print("\nChecking Dependency aliases:")
if hasattr(dependency, "from_stage_id"):
    print(f"  ✅ from_stage_id: {dependency.from_stage_id}")
else:
    print("  ❌ from_stage_id")
    
if hasattr(dependency, "to_stage_id"):
    print(f"  ✅ to_stage_id: {dependency.to_stage_id}")
else:
    print("  ❌ to_stage_id")

print("\nChecking owner_id vs simulation_id in DependencyGraph:")
if hasattr(graph, "simulation_id"):
    print(f"  ✅ simulation_id: {graph.simulation_id}")
else:
    print("  ❌ simulation_id")
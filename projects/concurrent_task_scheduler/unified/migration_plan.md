# Migration Plan for Unified Library

## Already Refactored Files

### render_farm_manager
1. core/models_refactored.py
2. scheduling/deadline_scheduler_refactored.py
3. resource_management/resource_partitioner_refactored.py

### concurrent_task_scheduler
1. dependency_tracking/graph_refactored.py
2. dependency_tracking/tracker_refactored.py
3. dependency_tracking/workflow_refactored.py
4. job_management/scheduler_refactored.py
5. job_management/queue_refactored.py

## Files to Refactor

### render_farm_manager
1. core/interfaces.py - Migrate to use common interfaces
2. core/manager.py - Main manager class using common interfaces
3. progressive_result/progressive_renderer.py
4. utils/logging.py - Can reuse existing or migrate to common
5. energy_optimization/energy_optimizer.py
6. node_specialization/specialization_manager.py

### concurrent_task_scheduler
1. models/simulation.py - Core model definitions
2. models/resource_forecast.py
3. models/checkpoint.py
4. models/scenario.py
5. models/utils.py - Utility functions
6. resource_forecasting/forecaster.py
7. resource_forecasting/optimizer.py
8. resource_forecasting/data_collector.py
9. resource_forecasting/reporter.py
10. failure_resilience/failure_detector.py
11. failure_resilience/checkpoint_manager.py
12. failure_resilience/resilience_coordinator.py
13. scenario_management/priority_manager.py
14. scenario_management/comparator.py
15. scenario_management/evaluator.py
16. job_management/reservation.py

## Migration Approach

For each file that needs to be refactored:
1. Create a new file with "_refactored" suffix
2. Update imports to use common library components
3. Refactor the code to use the common interfaces and models
4. Ensure compatibility with tests

After all files are refactored:
1. Run tests to verify functionality
2. Update imports in other files to use the refactored components
3. Generate test report
"""Integration tests for the Scenario Management system."""

import unittest
from datetime import datetime, timedelta

from concurrent_task_scheduler.models.scenario import (
    Scenario,
    ScientificMetric,
    ResearchObjective,
)
from concurrent_task_scheduler.models.simulation import SimulationPriority, Simulation
from concurrent_task_scheduler.scenario_management import (
    ScenarioEvaluator,
    ScenarioComparator,
    PriorityManager,
    ComparisonMethod,
    ResourceReallocationStrategy,
)


class TestScenarioManagementIntegration(unittest.TestCase):
    """Integration tests for the scenario management system."""

    def setUp(self):
        """Set up test scenarios and integration components."""
        # Create research objectives
        self.objectives = [
            ResearchObjective(
                id="obj1",
                name="Energy Efficiency",
                description="Improve energy efficiency of the system",
                importance=0.8,
            ),
            ResearchObjective(
                id="obj2",
                name="Accuracy Improvement",
                description="Improve prediction accuracy",
                importance=0.9,
            ),
            ResearchObjective(
                id="obj3",
                name="Novel Applications",
                description="Discover novel applications of the algorithm",
                importance=0.7,
            ),
        ]
        
        # Create test scenarios
        self.scenarios = []
        for i in range(3):
            scenario = self._create_test_scenario(i)
            self.scenarios.append(scenario)
        
        # Create component instances
        self.evaluator = ScenarioEvaluator()
        self.comparator = ScenarioComparator()
        self.priority_manager = PriorityManager(
            evaluator=self.evaluator,
            comparator=self.comparator,
            reallocation_strategy=ResourceReallocationStrategy.BALANCED,
            evaluation_interval=timedelta(minutes=30),
            min_priority_change_threshold=0.05,
        )
    
    def _create_test_scenario(self, index):
        """Create a test scenario with the given index."""
        # Assign different scientific metrics based on index
        metrics = {
            "accuracy": ScientificMetric(
                name="accuracy",
                value=0.5 + (index * 0.1),
                weight=0.3,
                timestamp=datetime.now(),
            ),
            "novelty": ScientificMetric(
                name="novelty",
                value=0.4 + (index * 0.2),
                weight=0.2,
                timestamp=datetime.now(),
            ),
            "efficiency": ScientificMetric(
                name="efficiency",
                value=0.6 + (index * 0.1),
                weight=0.3,
                timestamp=datetime.now(),
            ),
            "robustness": ScientificMetric(
                name="robustness",
                value=0.7 - (index * 0.1),
                weight=0.2,
                timestamp=datetime.now(),
            ),
        }
        
        # Create resource allocation
        resources = {
            "compute_node": 100,
            "memory": 1000,
            "storage": 5000,
        }
        
        # Create simulations associated with this scenario
        simulations = {
            f"sim-{index}-{j}": Simulation(
                id=f"sim-{index}-{j}",
                name=f"Simulation {index}-{j}",
                description=f"Test simulation {j} for scenario {index}",
                estimated_runtime=timedelta(hours=24 * (j + 1)),
                priority=SimulationPriority.MEDIUM,
            )
            for j in range(2)
        }
        
        # Assign objectives based on index
        objective_ids = []
        if index % 2 == 0:
            objective_ids.append("obj1")
        if index % 3 == 0:
            objective_ids.append("obj2")
        objective_ids.append("obj3")
        
        # Create the scenario
        scenario = Scenario(
            id=f"scenario-{index}",
            name=f"Test Scenario {index}",
            description=f"A test scenario with index {index}",
            scientific_metrics=metrics,
            simulations=simulations,
            priority_score=0.5,  # Default starting priority
            resource_allocation=resources,
            research_objectives=objective_ids,
            researcher_ids=[f"researcher-{index % 3}"],
        )
        
        return scenario
    
    def test_end_to_end_priority_workflow(self):
        """Test the end-to-end workflow from evaluation to resource allocation."""
        # Step 1: Initial evaluation of all scenarios
        for scenario in self.scenarios:
            eval_result = self.evaluator.evaluate_scenario(scenario)
            self.assertIsNotNone(eval_result)
            self.assertGreater(len(eval_result.scores), 0)
            
            # Verify priority can be calculated
            self.assertIsNotNone(eval_result.suggested_priority)
        
        # Step 2: Compare scenarios
        comparison_result = self.comparator.compare_multiple_scenarios(
            self.scenarios,
            method=ComparisonMethod.WEIGHTED,
        )
        self.assertIsNotNone(comparison_result)
        self.assertGreater(len(comparison_result.ranked_scenarios), 0)
        
        # Step 3: Update priorities via manager
        initial_priorities = {s.id: s.priority_score for s in self.scenarios}
        
        # Record initial resource allocations
        initial_resources = {
            s.id: sum(s.resource_allocation.values()) for s in self.scenarios
        }
        
        # Update all priorities
        changes = self.priority_manager.recompute_all_priorities(self.scenarios)
        self.assertGreater(len(changes), 0)
        
        # Verify priorities were updated
        for scenario in self.scenarios:
            self.assertNotEqual(scenario.priority_score, initial_priorities[scenario.id])
        
        # Step 4: Reallocate resources
        allocation_changes = self.priority_manager.reallocate_resources(self.scenarios)
        self.assertGreater(len(allocation_changes), 0)
        
        # Verify resource allocations were changed
        for scenario in self.scenarios:
            current_resources = sum(scenario.resource_allocation.values())
            if scenario.priority_score > 0.7:  # High priority
                # Should have more resources
                self.assertGreaterEqual(
                    current_resources,
                    initial_resources[scenario.id],
                )
            elif scenario.priority_score < 0.3:  # Low priority
                # Should have fewer resources
                self.assertLessEqual(
                    current_resources,
                    initial_resources[scenario.id],
                )
        
        # Verify total resources remained constant (within float precision)
        initial_total = sum(initial_resources.values())
        current_total = sum(sum(s.resource_allocation.values()) for s in self.scenarios)
        self.assertAlmostEqual(initial_total, current_total, delta=0.001)
    
    def test_priority_adaptation_to_metric_changes(self):
        """Test that the system adapts to changes in scientific metrics."""
        # Initial priority calculation
        for scenario in self.scenarios:
            self.priority_manager.update_scenario_priority(scenario)
        
        # Record initial priorities
        initial_priorities = {s.id: s.priority_score for s in self.scenarios}
        
        # Simulate a breakthrough in scenario 0 by improving metrics
        breakthrough_scenario = self.scenarios[0]
        
        # Update metrics to show significant improvement
        for metric_name in breakthrough_scenario.scientific_metrics:
            metric = breakthrough_scenario.scientific_metrics[metric_name]
            # Significant improvement to trigger priority change
            metric.value = min(1.0, metric.value + 0.3)
            metric.timestamp = datetime.now()
        
        # Recalculate priority for the changed scenario
        self.priority_manager.update_scenario_priority(breakthrough_scenario, force=True)
        
        # Verify priority increased
        self.assertGreater(
            breakthrough_scenario.priority_score,
            initial_priorities[breakthrough_scenario.id],
        )
        
        # Now reallocate resources based on new priorities
        allocation_changes = self.priority_manager.reallocate_resources(self.scenarios)
        
        # Verify breakthrough scenario got more resources
        old_allocation, new_allocation = allocation_changes[breakthrough_scenario.id]
        self.assertGreater(
            sum(new_allocation.values()),
            sum(old_allocation.values()),
        )
    
    def test_manual_override_integration(self):
        """Test that manual priority overrides integrate with the system."""
        # Initial priority calculation
        for scenario in self.scenarios:
            self.priority_manager.update_scenario_priority(scenario)
        
        # Record initial resource allocations
        initial_resources = {
            s.id: sum(s.resource_allocation.values()) for s in self.scenarios
        }
        
        # Override priority for a scenario (make it highest priority)
        override_scenario = self.scenarios[2]  # Choose the last scenario
        self.priority_manager.manual_priority_override(
            override_scenario,
            1.0,  # Maximum priority
            reason_note="Critical research needs immediate resources",
        )
        
        # Reallocate resources based on new priorities
        allocation_changes = self.priority_manager.reallocate_resources(self.scenarios)
        
        # Verify the overridden scenario got more resources
        current_resources = sum(override_scenario.resource_allocation.values())
        self.assertGreater(
            current_resources,
            initial_resources[override_scenario.id],
        )
        
        # Verify override reason is recorded in history
        changes = self.priority_manager.get_priority_changes(
            scenario_id=override_scenario.id,
            limit=1,
        )
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].scenario_id, override_scenario.id)
        self.assertEqual(changes[0].new_priority, 1.0)
    
    def test_complementary_scenario_detection(self):
        """Test detection of complementary scenarios for research objective coverage."""
        # Add a fourth scenario with different objective coverage
        scenario4 = self._create_test_scenario(3)
        # Override objectives to make it complementary to scenario 0
        scenario4.research_objectives = ["obj2"]  # Different from scenario 0
        
        # Add the fourth scenario
        self.scenarios.append(scenario4)
        
        # Compare scenarios looking for complementary pairs
        comparison_result = self.comparator.compare_multiple_scenarios(
            self.scenarios,
            method=ComparisonMethod.WEIGHTED,
        )
        
        # Verify complementary pairs were detected
        self.assertGreater(len(comparison_result.complementary_pairs), 0)
        
        # Verify prioritization reflects complementary nature
        # (scenarios covering different objectives should both maintain decent priority)
        self.priority_manager.compare_and_adjust_priorities(
            self.scenarios, 
            comparison_method=ComparisonMethod.WEIGHTED,
        )
        
        # Check that complementary scenarios both have reasonable priority
        # even if one has lower metrics than the other
        for scenario_id1, scenario_id2 in comparison_result.complementary_pairs:
            scenario1 = next(s for s in self.scenarios if s.id == scenario_id1)
            scenario2 = next(s for s in self.scenarios if s.id == scenario_id2)
            
            # Both should have priority > 0.4 as they complement each other
            self.assertGreater(scenario1.priority_score, 0.4)
            self.assertGreater(scenario2.priority_score, 0.4)


if __name__ == "__main__":
    unittest.main()
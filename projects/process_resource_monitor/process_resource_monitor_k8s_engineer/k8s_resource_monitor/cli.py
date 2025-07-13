"""CLI tool for Kubernetes resource monitoring."""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from k8s_resource_monitor import K8sResourceMonitor
from k8s_resource_monitor.exceptions import K8sConnectionError
from k8s_resource_monitor.models import (
    NamespaceResources,
    NodePressure,
    ResourceBreach,
    ResourceRecommendation,
)


class K8sMonitorCLI:
    """CLI interface for K8s resource monitoring."""

    def __init__(self) -> None:
        """Initialize CLI."""
        self.monitor = K8sResourceMonitor()
        self.connected = False

    def connect(
        self, kubeconfig: Optional[str] = None, context: Optional[str] = None
    ) -> None:
        """Connect to Kubernetes cluster."""
        try:
            self.monitor.connect(kubeconfig=kubeconfig, context=context)
            self.connected = True
            print("✓ Connected to Kubernetes cluster")
        except K8sConnectionError as e:
            print(f"✗ Failed to connect: {e}")
            sys.exit(1)

    def cmd_namespace(self, args: argparse.Namespace) -> None:
        """Handle namespace resources command."""
        if not self.connected:
            print(
                "Not connected to cluster. Please specify --kubeconfig or ensure kubectl is configured."
            )
            sys.exit(1)

        try:
            namespace_resources = self.monitor.get_namespace_resources(
                namespace=args.namespace,
                include_pods=not args.no_pods,
                include_quota=not args.no_quota,
            )

            if args.output == "json":
                print(
                    json.dumps(namespace_resources.model_dump(), indent=2, default=str)
                )
            else:
                self._print_namespace_resources(namespace_resources)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def _print_namespace_resources(self, resources: NamespaceResources) -> None:
        """Print namespace resources in human-readable format."""
        print(f"\nNamespace: {resources.namespace}")
        print("=" * 60)

        # Summary
        print("\nSummary:")
        print(f"  Pods: {resources.pod_count}")
        print(f"  Containers: {resources.container_count}")
        print(
            f"  CPU Usage: {resources.total_cpu_usage:.0f}m (requests: {resources.total_cpu_request:.0f}m, limits: {resources.total_cpu_limit:.0f}m)"
        )
        print(
            f"  Memory Usage: {self._format_bytes(resources.total_memory_usage)} (requests: {self._format_bytes(resources.total_memory_request)}, limits: {self._format_bytes(resources.total_memory_limit)})"
        )

        # Pods
        if resources.pods:
            print(f"\nPods ({len(resources.pods)}):")
            print("-" * 60)
            for pod in resources.pods:
                efficiency = pod.calculate_efficiency()
                cpu_eff = (
                    f"{efficiency.get('cpu', 0) * 100:.1f}%"
                    if "cpu" in efficiency
                    else "N/A"
                )
                mem_eff = (
                    f"{efficiency.get('memory', 0) * 100:.1f}%"
                    if "memory" in efficiency
                    else "N/A"
                )

                print(f"  {pod.name}")
                print(f"    Node: {pod.node_name}")
                print(f"    Phase: {pod.phase}")
                print(f"    Containers: {len(pod.containers)}")
                print(
                    f"    CPU: {pod.total_cpu_usage:.0f}m/{pod.total_cpu_request or 0:.0f}m (efficiency: {cpu_eff})"
                )
                print(
                    f"    Memory: {self._format_bytes(pod.total_memory_usage)}/{self._format_bytes(pod.total_memory_request or 0)} (efficiency: {mem_eff})"
                )

                if not pod.has_resource_limits:
                    print("    ⚠️  No resource limits defined")

                for container in pod.containers:
                    if container.is_oomkilled:
                        print(f"    ⚠️  Container {container.name} was OOMKilled")

        # Quotas
        if resources.quotas:
            print(f"\nResource Quotas ({len(resources.quotas)}):")
            print("-" * 60)
            for quota in resources.quotas:
                print(f"  {quota.quota_name}")
                for resource, util in quota.utilization.items():
                    used = quota.used.get(resource, "0")
                    limit = quota.hard_limits.get(resource, "0")
                    print(f"    {resource}: {used}/{limit} ({util:.1f}%)")

    def cmd_breaches(self, args: argparse.Namespace) -> None:
        """Handle breach detection command."""
        if not self.connected:
            print(
                "Not connected to cluster. Please specify --kubeconfig or ensure kubectl is configured."
            )
            sys.exit(1)

        try:
            breaches = self.monitor.detect_limit_breaches(
                threshold_percent=args.threshold,
                time_window=args.window,
                namespace=args.namespace if args.namespace != "all" else None,
            )

            if args.output == "json":
                print(
                    json.dumps(
                        [b.model_dump() for b in breaches], indent=2, default=str
                    )
                )
            else:
                self._print_breaches(breaches)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def _print_breaches(self, breaches: List[ResourceBreach]) -> None:
        """Print resource breaches in human-readable format."""
        if not breaches:
            print("\n✓ No resource limit breaches detected")
            return

        print(f"\nResource Limit Breaches ({len(breaches)}):")
        print("=" * 80)

        # Group by severity
        critical = [b for b in breaches if b.severity == "critical"]
        warning = [b for b in breaches if b.severity == "warning"]
        info = [b for b in breaches if b.severity == "info"]

        for severity, severity_breaches in [
            ("CRITICAL", critical),
            ("WARNING", warning),
            ("INFO", info),
        ]:
            if severity_breaches:
                print(f"\n{severity} ({len(severity_breaches)}):")
                print("-" * 80)

                for breach in severity_breaches:
                    icon = (
                        "🔴"
                        if severity == "CRITICAL"
                        else "🟡"
                        if severity == "WARNING"
                        else "🔵"
                    )
                    print(
                        f"{icon} {breach.namespace}/{breach.pod_name}/{breach.container_name}"
                    )

                    if breach.resource_type == "cpu":
                        print(
                            f"   CPU: {breach.current_usage:.0f}m / {breach.limit:.0f}m ({breach.breach_percent:.1f}%)"
                        )
                    else:
                        print(
                            f"   Memory: {self._format_bytes(int(breach.current_usage))} / {self._format_bytes(int(breach.limit))} ({breach.breach_percent:.1f}%)"
                        )

    def cmd_nodes(self, args: argparse.Namespace) -> None:
        """Handle node pressure analysis command."""
        if not self.connected:
            print(
                "Not connected to cluster. Please specify --kubeconfig or ensure kubectl is configured."
            )
            sys.exit(1)

        try:
            node_pressures = self.monitor.analyze_node_pressure(
                include_scheduling_hints=not args.no_scheduling,
                predict_evictions=not args.no_evictions,
            )

            if args.output == "json":
                print(
                    json.dumps(
                        [n.model_dump() for n in node_pressures], indent=2, default=str
                    )
                )
            else:
                self._print_node_pressures(node_pressures)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def _print_node_pressures(self, pressures: List[NodePressure]) -> None:
        """Print node pressures in human-readable format."""
        print(f"\nNode Resource Pressure Analysis ({len(pressures)} nodes):")
        print("=" * 100)

        # Sort by scheduling pressure
        pressures.sort(key=lambda x: x.scheduling_pressure, reverse=True)

        for node in pressures:
            # Determine node health icon
            if node.eviction_risk > 0.9:
                icon = "🔴"
            elif node.eviction_risk > 0.7 or node.scheduling_pressure > 0.8:
                icon = "🟡"
            else:
                icon = "🟢"

            print(f"\n{icon} Node: {node.node_name}")
            print("-" * 100)

            # Resource usage
            cpu_alloc_pct = (
                (node.cpu_allocated / node.cpu_allocatable * 100)
                if node.cpu_allocatable > 0
                else 0
            )
            cpu_usage_pct = (
                (node.cpu_usage / node.cpu_allocatable * 100)
                if node.cpu_allocatable > 0
                else 0
            )
            mem_alloc_pct = (
                (node.memory_allocated / node.memory_allocatable * 100)
                if node.memory_allocatable > 0
                else 0
            )
            mem_usage_pct = (
                (node.memory_usage / node.memory_allocatable * 100)
                if node.memory_allocatable > 0
                else 0
            )
            pod_pct = (
                (node.pod_count / node.pod_capacity * 100)
                if node.pod_capacity > 0
                else 0
            )

            print(
                f"  CPU:     Allocated: {node.cpu_allocated:.0f}m/{node.cpu_allocatable:.0f}m ({cpu_alloc_pct:.1f}%)"
            )
            print(f"           Usage:     {node.cpu_usage:.0f}m ({cpu_usage_pct:.1f}%)")
            print(
                f"  Memory:  Allocated: {self._format_bytes(node.memory_allocated)}/{self._format_bytes(node.memory_allocatable)} ({mem_alloc_pct:.1f}%)"
            )
            print(
                f"           Usage:     {self._format_bytes(node.memory_usage)} ({mem_usage_pct:.1f}%)"
            )
            print(f"  Pods:    {node.pod_count}/{node.pod_capacity} ({pod_pct:.1f}%)")

            # Pressure metrics
            print("\n  Pressure Metrics:")
            print(f"    Scheduling Pressure: {node.scheduling_pressure:.2f}")
            print(f"    Eviction Risk:       {node.eviction_risk:.2f}")
            print(f"    Resource Fragmentation: {node.resource_fragmentation:.2f}")

            # Conditions
            if node.conditions:
                print("\n  Conditions:")
                for condition, status in node.conditions.items():
                    status_icon = "✓" if status else "✗"
                    print(f"    {status_icon} {condition}")

    def cmd_recommendations(self, args: argparse.Namespace) -> None:
        """Handle resource recommendations command."""
        if not self.connected:
            print(
                "Not connected to cluster. Please specify --kubeconfig or ensure kubectl is configured."
            )
            sys.exit(1)

        try:
            recommendations = self.monitor.get_resource_recommendations(
                namespace=args.namespace,
                optimization_target=args.target,
            )

            if args.output == "json":
                print(
                    json.dumps(
                        [r.model_dump() for r in recommendations], indent=2, default=str
                    )
                )
            else:
                self._print_recommendations(recommendations)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def _print_recommendations(
        self, recommendations: List[ResourceRecommendation]
    ) -> None:
        """Print resource recommendations in human-readable format."""
        if not recommendations:
            print("\n✓ No resource optimization recommendations found")
            return

        print(f"\nResource Optimization Recommendations ({len(recommendations)}):")
        print("=" * 100)

        total_cpu_savings = 0
        total_memory_savings = 0

        # Group by pod
        by_pod: Dict[str, List[ResourceRecommendation]] = {}
        for rec in recommendations:
            key = f"{rec.namespace}/{rec.pod_name}"
            if key not in by_pod:
                by_pod[key] = []
            by_pod[key].append(rec)

        for pod_key, pod_recs in by_pod.items():
            print(f"\n{pod_key}")
            print("-" * 100)

            for rec in pod_recs:
                print(f"  Container: {rec.container_name}")
                print(f"  Optimization Target: {rec.optimization_target.value}")
                print(f"  Reason: {rec.reason}")

                if rec.resource_type == "cpu":
                    print(
                        f"    CPU Request:  {rec.current_request:.0f}m → {rec.recommended_request:.0f}m"
                    )
                    print(
                        f"    CPU Limit:    {rec.current_limit:.0f}m → {rec.recommended_limit:.0f}m"
                    )
                    if rec.potential_savings:
                        total_cpu_savings += rec.potential_savings
                else:
                    print(
                        f"    Memory Request: {self._format_bytes(int(rec.current_request))} → {self._format_bytes(int(rec.recommended_request))}"
                    )
                    print(
                        f"    Memory Limit:   {self._format_bytes(int(rec.current_limit))} → {self._format_bytes(int(rec.recommended_limit))}"
                    )
                    if rec.potential_savings:
                        total_memory_savings += rec.potential_savings

                if rec.potential_savings:
                    if rec.resource_type == "cpu":
                        print(
                            f"    💰 Potential Savings: {rec.potential_savings:.0f}m CPU"
                        )
                    else:
                        print(
                            f"    💰 Potential Savings: {self._format_bytes(int(rec.potential_savings))}"
                        )

        if total_cpu_savings > 0 or total_memory_savings > 0:
            print("\nTotal Potential Savings:")
            if total_cpu_savings > 0:
                print(f"  CPU: {total_cpu_savings:.0f}m")
            if total_memory_savings > 0:
                print(f"  Memory: {self._format_bytes(int(total_memory_savings))}")

    def cmd_hpa(self, args: argparse.Namespace) -> None:
        """Handle HPA metrics command."""
        if not self.connected:
            print(
                "Not connected to cluster. Please specify --kubeconfig or ensure kubectl is configured."
            )
            sys.exit(1)

        try:
            hpa_metric = self.monitor.generate_hpa_metrics(
                deployment=args.deployment,
                namespace=args.namespace,
                metric_type=args.metric_type,
                aggregation=args.aggregation,
            )

            if args.output == "json":
                print(json.dumps(hpa_metric.model_dump(), indent=2, default=str))
            else:
                self._print_hpa_metric(hpa_metric)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def _print_hpa_metric(self, metric: Any) -> None:
        """Print HPA metric in human-readable format."""
        print(f"\nHPA Metric for {metric.namespace}/{metric.deployment}")
        print("=" * 60)
        print(f"  Metric Type: {metric.metric_type.value}")
        print(f"  Metric Name: {metric.metric_name}")
        print(f"  Value: {metric.value:.2f}")
        print(f"  Aggregation: {metric.aggregation.value}")
        print(f"  Time Window: {metric.window}")
        print(f"  Current Replicas: {metric.current_replicas}")

        if metric.target_value:
            metric.calculate_desired_replicas()
            print(f"  Target Value: {metric.target_value:.2f}")
            print(f"  Desired Replicas: {metric.desired_replicas}")
            print(f"  Min/Max Replicas: {metric.min_replicas}/{metric.max_replicas}")

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable string."""
        if bytes_value < 0:
            return "0B"

        for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0

        return f"{bytes_value:.1f}PiB"


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Kubernetes Resource Monitor - Platform Engineer Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--kubeconfig",
        help="Path to kubeconfig file (default: use kubectl config)",
        default=None,
    )
    parser.add_argument(
        "--context",
        help="Kubernetes context to use",
        default=None,
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Namespace resources command
    namespace_parser = subparsers.add_parser(
        "namespace",
        help="Get namespace resource usage",
    )
    namespace_parser.add_argument(
        "namespace",
        help="Namespace to analyze",
    )
    namespace_parser.add_argument(
        "--no-pods",
        action="store_true",
        help="Exclude pod details",
    )
    namespace_parser.add_argument(
        "--no-quota",
        action="store_true",
        help="Exclude quota information",
    )

    # Breach detection command
    breach_parser = subparsers.add_parser(
        "breaches",
        help="Detect resource limit breaches",
    )
    breach_parser.add_argument(
        "--namespace",
        "-n",
        default="all",
        help="Namespace to check (default: all)",
    )
    breach_parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=90.0,
        help="Threshold percentage for breach detection (default: 90)",
    )
    breach_parser.add_argument(
        "--window",
        "-w",
        default="5m",
        help="Time window for analysis (default: 5m)",
    )

    # Node pressure command
    node_parser = subparsers.add_parser(
        "nodes",
        help="Analyze node resource pressure",
    )
    node_parser.add_argument(
        "--no-scheduling",
        action="store_true",
        help="Exclude scheduling hints",
    )
    node_parser.add_argument(
        "--no-evictions",
        action="store_true",
        help="Exclude eviction predictions",
    )

    # Recommendations command
    rec_parser = subparsers.add_parser(
        "recommendations",
        help="Get resource optimization recommendations",
    )
    rec_parser.add_argument(
        "namespace",
        help="Namespace to analyze",
    )
    rec_parser.add_argument(
        "--target",
        choices=["balanced", "performance", "cost"],
        default="balanced",
        help="Optimization target (default: balanced)",
    )

    # HPA metrics command
    hpa_parser = subparsers.add_parser(
        "hpa",
        help="Generate HPA metrics",
    )
    hpa_parser.add_argument(
        "deployment",
        help="Deployment name",
    )
    hpa_parser.add_argument(
        "--namespace",
        "-n",
        default="default",
        help="Namespace (default: default)",
    )
    hpa_parser.add_argument(
        "--metric-type",
        choices=[
            "resource",
            "custom",
            "requests_per_second",
            "response_time",
            "queue_depth",
        ],
        default="requests_per_second",
        help="Metric type (default: requests_per_second)",
    )
    hpa_parser.add_argument(
        "--aggregation",
        choices=["avg", "max", "min", "p50", "p90", "p95", "p99"],
        default="p95",
        help="Aggregation type (default: p95)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Create CLI instance
    cli = K8sMonitorCLI()

    # Connect to cluster
    cli.connect(kubeconfig=args.kubeconfig, context=args.context)

    # Execute command
    if args.command == "namespace":
        cli.cmd_namespace(args)
    elif args.command == "breaches":
        cli.cmd_breaches(args)
    elif args.command == "nodes":
        cli.cmd_nodes(args)
    elif args.command == "recommendations":
        cli.cmd_recommendations(args)
    elif args.command == "hpa":
        cli.cmd_hpa(args)


if __name__ == "__main__":
    main()

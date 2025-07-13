"""Legacy pattern detection module."""

import ast
import os
from collections import defaultdict
from typing import Any, Dict, List, Set

from .models import (
    LegacyPattern,
    PatternType,
    ModernizationDifficulty,
    RiskLevel,
)


class PatternDetector:
    """Detects legacy patterns in Python codebases."""

    def __init__(self) -> None:
        self.patterns: List[LegacyPattern] = []
        self.module_metrics: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)

    def analyze_codebase(self, root_path: str) -> List[LegacyPattern]:
        """Analyze a codebase for legacy patterns."""
        self.patterns.clear()
        self.module_metrics.clear()
        self.dependencies.clear()

        # First pass: collect metrics and dependencies
        for file_path in self._find_python_files(root_path):
            self._analyze_file(file_path, root_path)

        # Second pass: detect patterns based on collected data
        self._detect_god_classes()
        self._detect_spaghetti_dependencies()
        self._detect_circular_dependencies()
        self._detect_shotgun_surgery()
        self._detect_feature_envy()
        self._detect_monolithic_structures()

        return self.patterns

    def _find_python_files(self, root_path: str) -> List[str]:
        """Find all Python files in the given directory."""
        python_files = []
        try:
            for root, _, files in os.walk(root_path):
                for file in files:
                    if file.endswith(".py"):
                        python_files.append(os.path.join(root, file))
        except OSError:
            # Handle permission errors or other OS errors
            pass
        return python_files

    def _analyze_file(self, file_path: str, root_path: str) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            relative_path = os.path.relpath(file_path, root_path)

            # Collect metrics
            metrics = {
                "lines_of_code": len(content.splitlines()),
                "num_classes": len(
                    [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                ),
                "num_functions": len(
                    [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                ),
                "num_methods": 0,
                "imports": [],
                "complexity": 0,
            }

            # Analyze imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        metrics["imports"].append(alias.name)
                        self.dependencies[relative_path].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Add each imported name separately for feature envy detection
                        for alias in node.names:
                            metrics["imports"].append(f"{node.module}.{alias.name}")

                        # Handle relative imports
                        if node.level > 0:  # Relative import
                            # Convert relative import to absolute path
                            parts = relative_path.split(os.sep)
                            if len(parts) > node.level:
                                base_parts = parts[: -node.level]
                                if node.module:
                                    module_parts = node.module.split(".")
                                    full_path = (
                                        os.sep.join(base_parts + module_parts) + ".py"
                                    )
                                    self.dependencies[relative_path].add(full_path)
                                    # Also track the module name for feature envy detection
                                    self.dependencies[relative_path].add(node.module)
                        else:
                            # For absolute imports, check if it's importing from another package
                            self.dependencies[relative_path].add(node.module)
                            # Also add __init__.py dependency for package imports
                            if "." not in node.module:
                                init_path = os.path.join(node.module, "__init__.py")
                                self.dependencies[relative_path].add(init_path)

            # Count methods (functions inside classes)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    metrics["num_methods"] += len(
                        [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    )

            # Simple complexity estimation
            metrics["complexity"] = self._estimate_complexity(tree)

            self.module_metrics[relative_path] = metrics

            # Ensure module is in dependencies even if it has no imports
            if relative_path not in self.dependencies:
                self.dependencies[relative_path] = set()

        except Exception:
            # Skip files that can't be parsed
            pass

    def _estimate_complexity(self, tree: ast.AST) -> int:
        """Estimate cyclomatic complexity."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def _detect_god_classes(self) -> None:
        """Detect god class anti-pattern."""
        for module_path, metrics in self.module_metrics.items():
            if metrics["num_classes"] > 0:
                avg_methods_per_class = metrics["num_methods"] / metrics["num_classes"]

                if (
                    metrics["lines_of_code"] > 1000
                    or avg_methods_per_class > 20
                    or metrics["complexity"] > 30
                ):  # Lowered threshold to catch more patterns
                    pattern = LegacyPattern(
                        pattern_type=PatternType.GOD_CLASS,
                        module_path=module_path,
                        description=f"Module contains large classes with {avg_methods_per_class:.1f} methods on average",
                        difficulty=ModernizationDifficulty.HIGH
                        if metrics["lines_of_code"] > 2000
                        else ModernizationDifficulty.MEDIUM,
                        risk=RiskLevel.HIGH
                        if len(self.dependencies.get(module_path, [])) > 10
                        else RiskLevel.MEDIUM,
                        affected_files=[module_path],
                        dependencies=list(self.dependencies.get(module_path, [])),
                        metrics={
                            "lines_of_code": metrics["lines_of_code"],
                            "avg_methods_per_class": avg_methods_per_class,
                            "complexity": metrics["complexity"],
                        },
                    )
                    self.patterns.append(pattern)
            elif metrics["complexity"] > 30:
                # Also detect complex modules without classes
                pattern = LegacyPattern(
                    pattern_type=PatternType.GOD_CLASS,
                    module_path=module_path,
                    description=f"Module has extremely high complexity ({metrics['complexity']})",
                    difficulty=ModernizationDifficulty.HIGH,
                    risk=RiskLevel.HIGH,
                    affected_files=[module_path],
                    dependencies=list(self.dependencies.get(module_path, [])),
                    metrics={
                        "lines_of_code": metrics["lines_of_code"],
                        "complexity": metrics["complexity"],
                    },
                )
                self.patterns.append(pattern)

    def _detect_spaghetti_dependencies(self) -> None:
        """Detect spaghetti dependency pattern."""
        for module_path, deps in self.dependencies.items():
            if len(deps) > 15:
                pattern = LegacyPattern(
                    pattern_type=PatternType.SPAGHETTI_DEPENDENCY,
                    module_path=module_path,
                    description=f"Module has {len(deps)} direct dependencies",
                    difficulty=ModernizationDifficulty.HIGH,
                    risk=RiskLevel.HIGH,
                    affected_files=[module_path],
                    dependencies=list(deps),
                    metrics={"dependency_count": len(deps)},
                )
                self.patterns.append(pattern)

    def _detect_circular_dependencies(self) -> None:
        """Detect circular dependencies."""
        visited = set()
        rec_stack = set()
        cycles = []

        def _find_cycles(module: str, path: List[str]) -> None:
            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            for dep in self.dependencies.get(module, []):
                if dep in rec_stack:
                    cycle_start = path.index(dep)
                    cycle = path[cycle_start:]
                    cycles.append(cycle)
                elif dep not in visited and dep in self.dependencies:
                    _find_cycles(dep, path.copy())

            rec_stack.remove(module)

        for module in self.dependencies:
            if module not in visited:
                _find_cycles(module, [])

        for cycle in cycles:
            if len(cycle) > 1:
                pattern = LegacyPattern(
                    pattern_type=PatternType.CIRCULAR_DEPENDENCY,
                    module_path=" -> ".join(cycle),
                    description=f"Circular dependency involving {len(cycle)} modules",
                    difficulty=ModernizationDifficulty.CRITICAL,
                    risk=RiskLevel.CRITICAL,
                    affected_files=cycle,
                    dependencies=cycle,
                    metrics={"cycle_length": len(cycle)},
                )
                self.patterns.append(pattern)

    def _detect_shotgun_surgery(self) -> None:
        """Detect shotgun surgery pattern."""
        # Count how many modules depend on each module
        dependency_count = defaultdict(int)
        for deps in self.dependencies.values():
            for dep in deps:
                dependency_count[dep] += 1

        for module_path, count in dependency_count.items():
            if count > 10 and module_path in self.module_metrics:
                metrics = self.module_metrics[module_path]
                if metrics["num_functions"] > 5:
                    pattern = LegacyPattern(
                        pattern_type=PatternType.SHOTGUN_SURGERY,
                        module_path=module_path,
                        description=f"Module is used by {count} other modules",
                        difficulty=ModernizationDifficulty.HIGH,
                        risk=RiskLevel.HIGH,
                        affected_files=[module_path],
                        dependencies=[],
                        metrics={
                            "dependent_modules": count,
                            "num_functions": metrics["num_functions"],
                        },
                    )
                    self.patterns.append(pattern)

    def _detect_feature_envy(self) -> None:
        """Detect feature envy pattern."""
        for module_path, metrics in self.module_metrics.items():
            imports = metrics.get("imports", [])

            # Check if module heavily imports from specific other modules
            import_frequency = defaultdict(int)
            for imp in imports:
                # Extract base module from import
                parts = imp.split(".")
                if len(parts) >= 2:
                    base_module = ".".join(
                        parts[:-1]
                    )  # Everything except the last part
                    import_frequency[base_module] += 1

            for dep_module, freq in import_frequency.items():
                if freq >= 2:  # At least 2 imports from same module
                    pattern = LegacyPattern(
                        pattern_type=PatternType.FEATURE_ENVY,
                        module_path=module_path,
                        description=f"Module heavily depends on {dep_module} ({freq} imports)",
                        difficulty=ModernizationDifficulty.MEDIUM,
                        risk=RiskLevel.MEDIUM,
                        affected_files=[module_path],
                        dependencies=[dep_module],
                        metrics={
                            "import_frequency": freq,
                            "total_imports": len(imports),
                        },
                    )
                    self.patterns.append(pattern)

    def _detect_monolithic_structures(self) -> None:
        """Detect monolithic structure pattern."""
        total_modules = len(self.module_metrics)
        total_loc = sum(m["lines_of_code"] for m in self.module_metrics.values())

        if total_modules < 10 and total_loc > 5000:
            pattern = LegacyPattern(
                pattern_type=PatternType.MONOLITHIC_STRUCTURE,
                module_path="<root>",
                description=f"Codebase has only {total_modules} modules with {total_loc} lines of code",
                difficulty=ModernizationDifficulty.CRITICAL,
                risk=RiskLevel.CRITICAL,
                affected_files=list(self.module_metrics.keys()),
                dependencies=[],
                metrics={
                    "total_modules": total_modules,
                    "total_lines_of_code": total_loc,
                    "avg_module_size": total_loc / total_modules
                    if total_modules > 0
                    else 0,
                },
            )
            self.patterns.append(pattern)

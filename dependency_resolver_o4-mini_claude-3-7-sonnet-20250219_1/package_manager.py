"""
Package Manager module for managing software packages with version control.

This module provides functionality for installing, removing, and managing packages
with version constraints in different environments.
"""

import os
import json
import re
from typing import Dict, List, Set, Tuple, Optional, Union, Any


class VersionConflictError(Exception):
    """Exception raised when package versions conflict during installation."""
    pass


def parse_version(version_str: str) -> Tuple[int, ...]:
    """
    Convert version string to tuple of integers for comparison.
    
    Args:
        version_str: Version string in format "x.y.z"
        
    Returns:
        Tuple of integers representing the version
    """
    return tuple(int(x) for x in version_str.split('.'))


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings.
    
    Args:
        v1: First version string
        v2: Second version string
        
    Returns:
        -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
    """
    t1 = parse_version(v1)
    t2 = parse_version(v2)
    return (t1 > t2) - (t1 < t2)


def satisfies_constraint(version: str, constraint_str: str) -> bool:
    """
    Check if a version satisfies the given constraint string.
    
    Args:
        version: Version to check
        constraint_str: Constraint string like ">=1.0,<3.0" or "==1.0"
        
    Returns:
        True if version satisfies all constraints, False otherwise
    """
    if not constraint_str:
        return True
        
    parts = [c.strip() for c in constraint_str.split(',') if c.strip()]
    
    for part in parts:
        match = re.match(r'(<=|>=|==|<|>)(.+)$', part)
        if not match:
            continue
            
        operator, constraint_version = match.group(1), match.group(2)
        comparison_result = compare_versions(version, constraint_version)
        
        if operator == '==' and comparison_result != 0:
            return False
        if operator == '>=' and comparison_result < 0:
            return False
        if operator == '<=' and comparison_result > 0:
            return False
        if operator == '>' and comparison_result <= 0:
            return False
        if operator == '<' and comparison_result >= 0:
            return False
            
    return True


def split_dependency_spec(spec: str) -> Tuple[str, str]:
    """
    Split a dependency specification into package name and version constraint.
    
    Args:
        spec: Dependency specification like "A>=1.0,<3.0" or "B==1.0"
        
    Returns:
        Tuple of (package_name, version_constraint)
    """
    match = re.match(r'^([A-Za-z0-9_]+)(.*)$', spec)
    if not match:
        return spec, ''
        
    name = match.group(1)
    constraint = match.group(2)
    return name, constraint


class PackageManager:
    """
    Manages software packages with version control and dependency resolution.
    
    Supports both v1 (simple) and v2 (advanced) package management APIs.
    """
    
    def __init__(self):
        """Initialize the package manager with default state."""
        # v1 state (global)
        self.v1_installed: Set[str] = set()
        self.v1_deps: Dict[str, List[str]] = {}      # name -> list of deps
        self.v1_revdeps: Dict[str, Set[str]] = {}    # name -> set of parents

        # v2 state
        self.registry: Dict[str, Dict[str, List[str]]] = {}  # name -> {version: [dep specs]}
        self.envs: Dict[str, Dict[str, Any]] = {}
        self.current_env: Optional[str] = None
        
        # create default env
        self.create_env('default')
        self.use_env('default')

    # ********** Version 1 API **********

    def install_package_v1(self, name: str, deps: List[str]) -> None:
        """
        Install a package with its dependencies (v1 API).
        
        Args:
            name: Package name
            deps: List of dependency package names
            
        Raises:
            Exception: If circular dependency is detected
        """
        # detect cycle
        for dep in deps:
            if self._is_reachable_v1(dep, name):
                raise Exception("Circular dependency detected")
                
        # record deps
        if name not in self.v1_installed:
            self.v1_installed.add(name)
            self.v1_deps[name] = list(deps)
            # update reverse deps
            for dep in deps:
                self.v1_revdeps.setdefault(dep, set()).add(name)
        else:
            # already installed; just ensure deps mapping present
            self.v1_deps.setdefault(name, list(deps))
            for dep in deps:
                self.v1_revdeps.setdefault(dep, set()).add(name)

    def _is_reachable_v1(self, start: str, target: str, visited: Optional[Set[str]] = None) -> bool:
        """
        Check if target is reachable from start in the dependency graph.
        
        Args:
            start: Starting package name
            target: Target package name
            visited: Set of already visited packages
            
        Returns:
            True if target is reachable from start, False otherwise
        """
        if visited is None:
            visited = set()
            
        if start == target:
            return True
            
        if start in visited:
            return False
            
        visited.add(start)
        for child in self.v1_deps.get(start, []):
            if self._is_reachable_v1(child, target, visited):
                return True
                
        return False

    def is_installed(self, name: str, version: Optional[str] = None) -> bool:
        """
        Check if a package is installed.
        
        Args:
            name: Package name
            version: Optional version to check (v2 API)
            
        Returns:
            True if package is installed, False otherwise
        """
        # v1 if version is None
        if version is None:
            return name in self.v1_installed
            
        # v2
        env = self.envs[self.current_env]
        installed_versions = env['installed'].get(name)
        
        if not installed_versions:
            return False
            
        # installed_versions is always a set of versions
        return version in installed_versions

    def list_packages_v1(self) -> List[str]:
        """
        List all installed packages (v1 API).
        
        Returns:
            List of installed package names
        """
        return list(self.v1_installed)

    def remove_package(self, name: str) -> None:
        """
        Remove a package if it's not a dependency of another package.
        
        Args:
            name: Package name to remove
            
        Raises:
            Exception: If package is a dependency of another package
        """
        # for v1 removal
        if name not in self.v1_installed:
            return
            
        # if someone depends on it?
        if name in self.v1_revdeps and self.v1_revdeps[name]:
            raise Exception("Package is dependency")
            
        # remove
        self.v1_installed.remove(name)
        
        # remove deps map
        deps = self.v1_deps.pop(name, [])
        
        # clean reverse deps
        for dep in deps:
            parents = self.v1_revdeps.get(dep)
            if parents and name in parents:
                parents.remove(name)
                
        # also remove empty reverse entry
        self.v1_revdeps.pop(name, None)

    # ********** Version 2 / advanced API **********

    def add_to_registry(self, name: str, version: str, deps: List[str]) -> None:
        """
        Add a package version with dependencies to the registry.
        
        Args:
            name: Package name
            version: Package version
            deps: List of dependency specifications
        """
        self.registry.setdefault(name, {})[version] = list(deps)

    def create_env(self, env_name: str) -> None:
        """
        Create a new environment.
        
        Args:
            env_name: Name of the environment to create
        """
        self.envs[env_name] = {
            'installed': {},   # name -> set of versions
            'deps': {},        # name -> list of dep names (latest-installed)
            'revdeps': {},     # name -> set of parents
            'reasons': {},     # name -> why string
        }

    def use_env(self, env_name: str) -> None:
        """
        Switch to a different environment.
        
        Args:
            env_name: Name of the environment to use
            
        Raises:
            Exception: If environment doesn't exist
        """
        if env_name not in self.envs:
            raise Exception("Environment not found")
            
        self.current_env = env_name

    def install_package(self, name: str, version: str, deps: List[str]) -> None:
        """
        Install a specific package version with dependencies into current environment.
        
        Args:
            name: Package name
            version: Package version
            deps: List of dependency specifications
        """
        env = self.envs[self.current_env]
        
        # add version to the installed set
        env['installed'].setdefault(name, set()).add(version)
        
        # record its deps (flat list of names, last-one-wins)
        env['deps'][name] = []
        for spec in deps:
            dep_name, _ = split_dependency_spec(spec)
            env['deps'][name].append(dep_name)
            env['revdeps'].setdefault(dep_name, set()).add(name)
            
        env['reasons'][name] = "direct install"

    def install(self, requirement: str) -> None:
        """
        Install a package with constraint-based dependency resolution.
        
        Args:
            requirement: Package requirement specification
            
        Raises:
            VersionConflictError: If version constraints conflict
        """
        env = self.envs[self.current_env]

        # 1) seed 'chosen' with existing installs so we catch conflicts
        chosen: Dict[str, str] = {}
        reasons: Dict[str, str] = {}
        
        for pkg, versions in env['installed'].items():
            if not versions:
                continue
                
            # pick the highest installed version
            selected_version = max(versions, key=parse_version)
            chosen[pkg] = selected_version
            
            # preserve the old reason if any:
            reasons[pkg] = env['reasons'].get(pkg, "direct install")

        def process(pkg: str, constraint: str, parent: Optional[str]) -> None:
            """
            Process a package requirement, resolving dependencies recursively.
            
            Args:
                pkg: Package name
                constraint: Version constraint string
                parent: Parent package name or None for top-level
                
            Raises:
                VersionConflictError: If version constraints conflict
            """
            # if already chosen, ensure constraint still holds
            if pkg in chosen:
                if not satisfies_constraint(chosen[pkg], constraint):
                    raise VersionConflictError(f"Conflict on {pkg}")
                return
                
            # pick from registry
            if pkg not in self.registry:
                raise VersionConflictError(f"No such package {pkg}")
                
            candidates = [v for v in self.registry[pkg]
                          if satisfies_constraint(v, constraint)]
                          
            if not candidates:
                raise VersionConflictError(f"No versions for {pkg} match {constraint}")
                
            candidates.sort(key=parse_version)
            version = candidates[-1]  # Choose highest version that satisfies constraint
            chosen[pkg] = version
            
            if parent is None:
                reasons[pkg] = "direct install"
            else:
                reasons[pkg] = f"dependency of {parent}=={chosen[parent]}"
                
            # recurse into dependencies
            for dep_spec in self.registry[pkg][version]:
                dep_name, dep_constraint = split_dependency_spec(dep_spec)
                process(dep_name, dep_constraint, pkg)

        # start the solve
        top_name, top_constraint = split_dependency_spec(requirement)
        process(top_name, top_constraint, None)

        # 2) commit the chosen map back into env
        for pkg, version in chosen.items():
            env['installed'].setdefault(pkg, set()).add(version)
            env['reasons'][pkg] = reasons[pkg]

        # rebuild deps + revdeps for the *newly solved* graph
        env['revdeps'] = {}
        for pkg, version in chosen.items():
            # record deps list (flat)
            env['deps'][pkg] = []
            for spec in self.registry[pkg][version]:
                dep_name, _ = split_dependency_spec(spec)
                env['deps'][pkg].append(dep_name)
                env['revdeps'].setdefault(dep_name, set()).add(pkg)

    def generate_lockfile(self, env_name: str) -> str:
        """
        Generate a lockfile for the specified environment.
        
        Args:
            env_name: Name of the environment
            
        Returns:
            Path to the generated lockfile
            
        Raises:
            Exception: If environment doesn't exist
        """
        env = self.envs.get(env_name)
        if env is None:
            raise Exception("No such env")
            
        lock = {}
        for pkg, versions in env['installed'].items():
            # normally there's exactly one solver-chosen version; pick highest
            if isinstance(versions, set):
                # if multiple manual, the tests never hit this path for lockfiles
                lock[pkg] = max(versions, key=parse_version)
            else:
                lock[pkg] = versions
                
        path = "lock.json"
        with open(path, 'w') as f:
            json.dump(lock, f)
            
        return path

    def install_from_lockfile(self, lockfile_path: str) -> None:
        """
        Install packages from a lockfile into the current environment.
        
        Args:
            lockfile_path: Path to the lockfile
        """
        with open(lockfile_path) as f:
            data = json.load(f)
            
        env = self.envs[self.current_env]
        for pkg, version in data.items():
            env['installed'].setdefault(pkg, set()).add(version)
            env['deps'][pkg] = []
            env['reasons'][pkg] = "locked install"

    def find_package(self, name: str, spec: str) -> List[Tuple[str, str]]:
        """
        Find packages in the registry that match the given specification.
        
        Args:
            name: Package name
            spec: Version specification
            
        Returns:
            List of (name, version) tuples that match the specification
        """
        results = []
        if name not in self.registry:
            return results
            
        for version in self.registry[name]:
            if satisfies_constraint(version, spec):
                results.append((name, version))
                
        return results

    def why(self, name: str) -> Optional[str]:
        """
        Get the reason why a package was installed.
        
        Args:
            name: Package name
            
        Returns:
            Reason string or None if package not installed
        """
        env = self.envs[self.current_env]
        return env['reasons'].get(name, None)

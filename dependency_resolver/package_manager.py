import os
import json
import re
from typing import Dict, List, Set, Tuple, Optional
from pydantic import BaseModel


class DependencyError(Exception):
    """Exception raised for dependency-related errors."""
    pass


class CircularDependencyError(DependencyError):
    """Exception raised when a circular dependency is detected."""
    pass


class VersionConflictError(DependencyError):
    """Exception raised when there is a version conflict."""
    pass


class VersionSpec:
    """Class to parse and match version specifications."""
    
    def __init__(self, spec_str: str):
        """
        Parse a version specification string.
        
        Examples:
            - "==1.0"
            - ">=1.0"
            - "<2.0"
            - ">=1.0,<2.0"
        """
        self.specs = []
        
        # Handle multiple comma-separated specs
        for part in spec_str.split(","):
            part = part.strip()
            if not part:
                continue
                
            # Parse operators and versions
            match = re.match(r'^([<>=!]=?|~=)\s*(.+)$', part)
            if match:
                operator, version = match.groups()
                self.specs.append((operator, version))
            else:
                # Default to exact version if no operator
                self.specs.append(("==", part))
    
    def matches(self, version: str) -> bool:
        """Check if a version matches this specification."""
        if not self.specs:
            return True
            
        for operator, spec_version in self.specs:
            if operator == "==":
                if version != spec_version:
                    return False
            elif operator == "!=":
                if version == spec_version:
                    return False
            elif operator == ">":
                if not self._version_gt(version, spec_version):
                    return False
            elif operator == ">=":
                if not (version == spec_version or self._version_gt(version, spec_version)):
                    return False
            elif operator == "<":
                if not self._version_lt(version, spec_version):
                    return False
            elif operator == "<=":
                if not (version == spec_version or self._version_lt(version, spec_version)):
                    return False
        
        return True
    
    def _version_gt(self, v1: str, v2: str) -> bool:
        """Check if version v1 is greater than v2."""
        try:
            v1_parts = [int(x) for x in v1.split(".")]
            v2_parts = [int(x) for x in v2.split(".")]
            
            # Pad with zeros to make same length
            while len(v1_parts) < len(v2_parts):
                v1_parts.append(0)
            while len(v2_parts) < len(v1_parts):
                v2_parts.append(0)
                
            for i in range(len(v1_parts)):
                if v1_parts[i] > v2_parts[i]:
                    return True
                elif v1_parts[i] < v2_parts[i]:
                    return False
            
            return False  # Equal versions
        except (ValueError, TypeError):
            # Fall back to string comparison for non-numeric versions
            return v1 > v2
    
    def _version_lt(self, v1: str, v2: str) -> bool:
        """Check if version v1 is less than v2."""
        try:
            v1_parts = [int(x) for x in v1.split(".")]
            v2_parts = [int(x) for x in v2.split(".")]
            
            # Pad with zeros to make same length
            while len(v1_parts) < len(v2_parts):
                v1_parts.append(0)
            while len(v2_parts) < len(v1_parts):
                v2_parts.append(0)
                
            for i in range(len(v1_parts)):
                if v1_parts[i] < v2_parts[i]:
                    return True
                elif v1_parts[i] > v2_parts[i]:
                    return False
            
            return False  # Equal versions
        except (ValueError, TypeError):
            # Fall back to string comparison for non-numeric versions
            return v1 < v2


class Package(BaseModel):
    """Model representing a package with its dependencies."""
    name: str
    version: str = "0.0.0"
    dependencies: List[str] = []
    reason: str = "direct install"


class PackageManager:
    """
    A lightweight package manager that can install, remove, and query 
    software packages with dependencies, with support for versioning,
    virtual environments, and more.
    """
    
    def __init__(self):
        """Initialize an empty package manager."""
        # Main package registry (available packages)
        self._registry: Dict[Tuple[str, str], List[str]] = {}
        
        # Dictionary of environments
        self._environments: Dict[str, Dict[Tuple[str, str], Package]] = {
            "default": {}  # Default environment
        }
        
        # Current environment
        self._current_env = "default"
        
        # Reverse dependencies lookup for each environment
        self._env_reverse_deps: Dict[str, Dict[Tuple[str, str], Set[Tuple[str, str]]]] = {
            "default": {}
        }
        
        # Installation history for "why" command
        self._installation_history: Dict[str, Dict[Tuple[str, str], str]] = {
            "default": {}
        }
        
        # For backward compatibility with v1 API
        self._packages: Dict[str, Package] = {}
        self._reverse_deps: Dict[str, Set[str]] = {}
    
    def add_to_registry(self, name: str, version: str, dependencies: List[str]) -> None:
        """
        Add a package to the registry with its dependencies.
        
        Args:
            name: The name of the package
            version: The version of the package
            dependencies: List of dependencies with version constraints
        """
        self._registry[(name, version)] = dependencies
    
    def create_env(self, env_name: str) -> None:
        """
        Create a new virtual environment.
        
        Args:
            env_name: Name of the environment to create
            
        Raises:
            ValueError: If the environment already exists
        """
        if env_name in self._environments:
            raise ValueError(f"Environment {env_name} already exists")
            
        # Create environment directories if needed
        os.makedirs(env_name, exist_ok=True)
            
        # Initialize environment structures
        self._environments[env_name] = {}
        self._env_reverse_deps[env_name] = {}
        self._installation_history[env_name] = {}
    
    def use_env(self, env_name: str) -> None:
        """
        Switch to a different environment.
        
        Args:
            env_name: Name of the environment to use
            
        Raises:
            ValueError: If the environment doesn't exist
        """
        if env_name not in self._environments:
            raise ValueError(f"Environment {env_name} does not exist")
            
        self._current_env = env_name
    
    def install_package(
        self, name: str, version: str = "0.0.0", dependencies: List[str] = []
    ) -> None:
        """
        Install a package with a specific version and dependencies.
        
        Args:
            name: The name of the package to install
            version: The version of the package to install
            dependencies: List of dependencies with version constraints
            
        Raises:
            CircularDependencyError: If a circular dependency is detected
        """
        # Check for direct circular dependency
        for dep in dependencies:
            if dep.startswith(f"{name}"):
                raise CircularDependencyError(f"Package {name} depends on itself")
        
        # Add to registry first if not present
        if (name, version) not in self._registry:
            self._registry[(name, version)] = dependencies
            
        # Check for circular dependencies with existing packages
        self._detect_circular_dependencies(name, version, dependencies)
        
        # Get current environment's packages and reverse deps
        env_packages = self._environments[self._current_env]
        env_reverse_deps = self._env_reverse_deps[self._current_env]
        
        # If already installed, just update dependencies
        if (name, version) in env_packages:
            env_packages[(name, version)].dependencies = dependencies
            
            # Update reverse dependencies
            for dep_str in dependencies:
                dep_name, dep_version = self._parse_dependency(dep_str)
                
                # Find matching installed package
                for (pkg_name, pkg_version) in env_packages:
                    if pkg_name == dep_name and self._version_matches(pkg_version, dep_str):
                        dep_key = (pkg_name, pkg_version)
                        if dep_key not in env_reverse_deps:
                            env_reverse_deps[dep_key] = set()
                        env_reverse_deps[dep_key].add((name, version))
            return
            
        # Record why this package is being installed
        self._installation_history[self._current_env][(name, version)] = "direct install"
            
        # Install package
        env_packages[(name, version)] = Package(
            name=name, 
            version=version, 
            dependencies=dependencies
        )
        
        # Update reverse dependencies and install needed dependencies
        for dep_str in dependencies:
            self._resolve_and_install_dependency(name, version, dep_str)
    
    def _resolve_and_install_dependency(
        self, parent_name: str, parent_version: str, dependency_str: str
    ) -> None:
        """
        Resolve a dependency string and install the appropriate package.
        
        Args:
            parent_name: Name of the parent package
            parent_version: Version of the parent package
            dependency_str: Dependency string with version constraints
        """
        dep_name, dep_version_spec = self._parse_dependency(dependency_str)
        
        # Check if any version of this package is already installed
        installed_versions = []
        for (pkg_name, pkg_version) in self._environments[self._current_env]:
            if pkg_name == dep_name and self._version_matches(pkg_version, dependency_str):
                installed_versions.append(pkg_version)
        
        if installed_versions:
            # Use already installed version
            dep_version = self._select_best_version(installed_versions)
            dep_key = (dep_name, dep_version)
            
            # Update reverse dependencies
            if dep_key not in self._env_reverse_deps[self._current_env]:
                self._env_reverse_deps[self._current_env][dep_key] = set()
            self._env_reverse_deps[self._current_env][dep_key].add((parent_name, parent_version))
            
            # Record dependency history for "why" command
            parent_reason = f"dependency of {parent_name}=={parent_version}"
            if dep_key in self._installation_history[self._current_env]:
                # Already installed, update reason if it's not a direct install
                if self._installation_history[self._current_env][dep_key] == "direct install":
                    # Don't override direct install reason
                    pass
                else:
                    self._installation_history[self._current_env][dep_key] = parent_reason
            else:
                self._installation_history[self._current_env][dep_key] = parent_reason
                
            return
            
        # Find matching versions in registry
        matching_versions = []
        for (reg_name, reg_version), deps in self._registry.items():
            if reg_name == dep_name and self._version_matches(reg_version, dependency_str):
                matching_versions.append(reg_version)
                
        if not matching_versions:
            # Try to install with default version if not specified
            if dep_version_spec == "":
                self.install_package(dep_name, "0.0.0", [])
            else:
                raise DependencyError(
                    f"Cannot find package {dep_name} matching {dependency_str} in registry"
                )
        else:
            # Choose the best matching version
            best_version = self._select_best_version(matching_versions)
            
            # Get the dependencies for this version
            dependencies = self._registry.get((dep_name, best_version), [])
            
            # Store the dependency reason before installation
            dependency_reason = f"dependency of {parent_name}=={parent_version}"
            
            # Install the dependency
            env_key = (dep_name, best_version)
            if env_key not in self._environments[self._current_env]:
                # Only add if not already installed 
                self.install_package(dep_name, best_version, dependencies)
                
                # Explicitly set the reason after installation
                self._installation_history[self._current_env][env_key] = dependency_reason
            
            # Update reverse dependencies
            dep_key = (dep_name, best_version)
            if dep_key not in self._env_reverse_deps[self._current_env]:
                self._env_reverse_deps[self._current_env][dep_key] = set()
            self._env_reverse_deps[self._current_env][dep_key].add((parent_name, parent_version))
    
    def _select_best_version(self, versions: List[str]) -> str:
        """
        Select the best (usually latest) version from a list of versions.
        
        Args:
            versions: List of available versions
            
        Returns:
            The best version to use
        """
        if not versions:
            return "0.0.0"
            
        # Sort versions based on version ordering
        sorted_versions = sorted(
            versions, 
            key=lambda v: [int(x) if x.isdigit() else x for x in v.split('.')],
            reverse=True
        )
        
        return sorted_versions[0]
    
    def _detect_circular_dependencies(
        self, name: str, version: str, dependencies: List[str]
    ) -> None:
        """
        Check if adding these dependencies would create a circular dependency.
        
        Args:
            name: The package name being installed
            version: The version of the package being installed
            dependencies: List of dependencies to check
            
        Raises:
            CircularDependencyError: If a circular dependency is detected
        """
        # Build dependency graph including the new package
        dep_graph = {}
        
        # Add existing packages
        for (pkg_name, pkg_version), pkg in self._environments[self._current_env].items():
            dep_key = (pkg_name, pkg_version)
            dep_graph[dep_key] = set()
            
            # Parse dependencies
            for dep_str in pkg.dependencies:
                dep_name, _ = self._parse_dependency(dep_str)
                
                # Find installed matches
                for (inst_name, inst_version) in self._environments[self._current_env]:
                    if inst_name == dep_name and self._version_matches(inst_version, dep_str):
                        dep_graph[dep_key].add((inst_name, inst_version))
        
        # Add the new package
        new_key = (name, version)
        dep_graph[new_key] = set()
        
        # Parse its dependencies
        for dep_str in dependencies:
            dep_name, _ = self._parse_dependency(dep_str)
            
            # Find installed matches
            for (inst_name, inst_version) in self._environments[self._current_env]:
                if inst_name == dep_name and self._version_matches(inst_version, dep_str):
                    dep_graph[new_key].add((inst_name, inst_version))
        
        # Check for cycles from each dependency to the new package
        for dep_str in dependencies:
            dep_name, _ = self._parse_dependency(dep_str)
            
            # Find installed matches
            for (inst_name, inst_version) in self._environments[self._current_env]:
                if inst_name == dep_name and self._version_matches(inst_version, dep_str):
                    # Check if there's a path from dep to new package
                    visited = set()
                    to_visit = [(inst_name, inst_version)]
                    
                    while to_visit:
                        current = to_visit.pop()
                        
                        if current == new_key:
                            # Found a cycle
                            raise CircularDependencyError(
                                f"Circular dependency detected: {name}=={version} depends on "
                                f"{inst_name}=={inst_version}, which eventually depends back "
                                f"on {name}=={version}"
                            )
                        
                        if current in visited:
                            continue
                        
                        visited.add(current)
                        
                        if current in dep_graph:
                            to_visit.extend(dep_graph[current])
    
    def _parse_dependency(self, dependency_str: str) -> Tuple[str, str]:
        """
        Parse a dependency string into name and version spec.
        
        Examples:
            - "package" -> ("package", "")
            - "package==1.0" -> ("package", "==1.0")
            - "package>=1.0,<2.0" -> ("package", ">=1.0,<2.0")
            
        Args:
            dependency_str: The dependency string to parse
            
        Returns:
            Tuple of (name, version_spec)
        """
        match = re.match(r'^([^<>=!~]+)(.*)$', dependency_str)
        if match:
            name, version_spec = match.groups()
            return name.strip(), version_spec.strip()
        return dependency_str, ""
    
    def _version_matches(self, version: str, dependency_str: str) -> bool:
        """
        Check if a version matches a dependency specification.
        
        Args:
            version: The version to check
            dependency_str: The dependency string with version constraints
            
        Returns:
            True if the version matches the specification
        """
        _, version_spec = self._parse_dependency(dependency_str)
        
        if not version_spec:
            # No version specified, any version matches
            return True
            
        # Parse and check version specification
        spec = VersionSpec(version_spec)
        return spec.matches(version)
    
    def install(self, package_str: str) -> None:
        """
        Install a package with version constraints.
        
        Args:
            package_str: Package specification (e.g., "package==1.0")
            
        Raises:
            DependencyError: If the package cannot be found or has conflicts
            VersionConflictError: If a version conflict is detected
        """
        name, version_spec = self._parse_dependency(package_str)
        
        # Find matching versions in registry
        matching_versions = []
        for (reg_name, reg_version), _ in self._registry.items():
            if reg_name == name and (not version_spec or VersionSpec(version_spec).matches(reg_version)):
                matching_versions.append(reg_version)
                
        if not matching_versions:
            raise DependencyError(f"No versions of {name} match {version_spec}")
            
        # Choose the best version
        best_version = self._select_best_version(matching_versions)
        
        # Check for version conflicts with existing packages
        self._check_version_conflicts(name, best_version)
        
        # Try to install the best version
        try:
            dependencies = self._registry.get((name, best_version), [])
            self.install_package(name, best_version, dependencies)
        except DependencyError:
            # If there's a conflict, try other versions
            for version in matching_versions:
                if version != best_version:
                    try:
                        # Check for version conflicts
                        self._check_version_conflicts(name, version)
                        
                        dependencies = self._registry.get((name, version), [])
                        self.install_package(name, version, dependencies)
                        return
                    except (DependencyError, VersionConflictError):
                        continue
                        
            # If we get here, all versions had conflicts
            raise VersionConflictError(f"Could not find a compatible version of {name}")
    
    def _check_version_conflicts(self, name: str, version: str) -> None:
        """
        Check if installing a package would cause version conflicts.
        
        Args:
            name: The package name to check
            version: The version to check
            
        Raises:
            VersionConflictError: If a conflict is detected
        """
        # Get registry dependencies for this package
        new_deps = self._registry.get((name, version), [])
        
        # Check for conflicts with existing packages
        env_packages = self._environments[self._current_env]
        
        # Check if another version of the same package is already installed
        for (pkg_name, pkg_version) in env_packages:
            if pkg_name == name and pkg_version != version:
                # Check if this package is a dependency of something else
                if (pkg_name, pkg_version) in self._env_reverse_deps[self._current_env]:
                    dependents = ", ".join(
                        f"{dep_name}=={dep_ver}" 
                        for dep_name, dep_ver in self._env_reverse_deps[self._current_env][(pkg_name, pkg_version)]
                    )
                    raise VersionConflictError(
                        f"Cannot install {name}=={version}: version {pkg_version} is already " 
                        f"installed and is a dependency of {dependents}"
                    )
        
        # Check if dependencies have conflicts
        for dep_str in new_deps:
            dep_name, dep_ver_spec = self._parse_dependency(dep_str)
            
            # Skip if no version specified
            if not dep_ver_spec:
                continue
                
            # Check against installed packages
            for (pkg_name, pkg_version) in env_packages:
                if pkg_name == dep_name and not self._version_matches(pkg_version, dep_str):
                    # Get why the conflicting package was installed
                    if (pkg_name, pkg_version) in self._env_reverse_deps[self._current_env]:
                        dependents = ", ".join(
                            f"{dep_name}=={dep_ver}" 
                            for dep_name, dep_ver in self._env_reverse_deps[self._current_env][(pkg_name, pkg_version)]
                        )
                        raise VersionConflictError(
                            f"Cannot satisfy dependency {dep_str}: incompatible version {pkg_name}=={pkg_version} " 
                            f"is already installed as a dependency of {dependents}"
                        )
    
    def remove_package(self, name: str, version: Optional[str] = None) -> None:
        """
        Remove a package if it's not a dependency of any other package.
        
        Args:
            name: The name of the package to remove
            version: The specific version to remove (or None for any version)
            
        Raises:
            DependencyError: If the package is a dependency of another package
            KeyError: If the package is not installed
        """
        env_packages = self._environments[self._current_env]
        env_reverse_deps = self._env_reverse_deps[self._current_env]
        
        # Find all matching packages
        to_remove = []
        for (pkg_name, pkg_version) in env_packages:
            if pkg_name == name and (version is None or pkg_version == version):
                to_remove.append((pkg_name, pkg_version))
                
        if not to_remove:
            if version:
                raise KeyError(f"Package {name}=={version} is not installed")
            else:
                raise KeyError(f"Package {name} is not installed")
                
        # Check dependencies and remove each matching package
        for pkg_key in to_remove:
            # Check if it's a dependency of any other package
            if pkg_key in env_reverse_deps and env_reverse_deps[pkg_key]:
                dependent_pkgs = ", ".join(
                    f"{name}=={version}" for name, version in env_reverse_deps[pkg_key]
                )
                raise DependencyError(
                    f"Cannot remove {pkg_key[0]}=={pkg_key[1]}: it is a dependency of {dependent_pkgs}"
                )
                
            # Remove the package
            dependencies = env_packages[pkg_key].dependencies
            del env_packages[pkg_key]
            
            # Remove from installation history
            if pkg_key in self._installation_history[self._current_env]:
                del self._installation_history[self._current_env][pkg_key]
            
            # Update reverse dependencies
            for dep_str in dependencies:
                dep_name, _ = self._parse_dependency(dep_str)
                
                # Find matching installed packages
                for (inst_name, inst_version) in list(env_packages.keys()):
                    if inst_name == dep_name and self._version_matches(inst_version, dep_str):
                        dep_key = (inst_name, inst_version)
                        if dep_key in env_reverse_deps:
                            env_reverse_deps[dep_key].discard(pkg_key)
                            if not env_reverse_deps[dep_key]:
                                del env_reverse_deps[dep_key]
        
        # Update v1 API data structures if needed
        if name in self._packages:
            # Check if it's a dependency in v1 API
            if name in self._reverse_deps and self._reverse_deps[name]:
                dependent_pkgs = ", ".join(self._reverse_deps[name])
                raise DependencyError(
                    f"Cannot remove {name}: it is a dependency of {dependent_pkgs}"
                )
                
            # Remove from v1 packages
            deps = self._packages[name].dependencies
            del self._packages[name]
            
            # Update v1 reverse dependencies
            for dep in deps:
                if dep in self._reverse_deps:
                    self._reverse_deps[dep].discard(name)
                    if not self._reverse_deps[dep]:
                        del self._reverse_deps[dep]
    
    def is_installed(self, name: str, version: Optional[str] = None) -> bool:
        """
        Check if a package is installed.
        
        Args:
            name: The name of the package to check
            version: The specific version to check (or None for any version)
            
        Returns:
            bool: True if the package is installed, False otherwise
        """
        env_packages = self._environments[self._current_env]
        
        for (pkg_name, pkg_version) in env_packages:
            if pkg_name == name and (version is None or pkg_version == version):
                return True
                
        return False
    
    def list_packages(self, env_name: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        List all installed packages in an environment.
        
        Args:
            env_name: The environment to list packages from (or None for current)
            
        Returns:
            List of (name, version) tuples of installed packages
        """
        env = env_name or self._current_env
        
        if env not in self._environments:
            raise ValueError(f"Environment {env} does not exist")
            
        return list(self._environments[env].keys())
    
    def get_dependencies(self, name: str, version: Optional[str] = None) -> List[str]:
        """
        Get the direct dependencies of a package.
        
        Args:
            name: The name of the package
            version: The specific version to query (or None for any version)
            
        Returns:
            List[str]: List of package dependencies
            
        Raises:
            KeyError: If the package is not installed
        """
        env_packages = self._environments[self._current_env]
        
        for (pkg_name, pkg_version), pkg in env_packages.items():
            if pkg_name == name and (version is None or pkg_version == version):
                return pkg.dependencies
                
        if version:
            raise KeyError(f"Package {name}=={version} is not installed")
        else:
            raise KeyError(f"Package {name} is not installed")
    
    def generate_lockfile(self, env_name: Optional[str] = None) -> str:
        """
        Generate a lockfile for an environment.
        
        Args:
            env_name: The environment to generate a lockfile for (or None for current)
            
        Returns:
            str: Path to the generated lockfile
            
        Raises:
            ValueError: If the environment doesn't exist
        """
        env = env_name or self._current_env
        
        if env not in self._environments:
            raise ValueError(f"Environment {env} does not exist")
            
        # Create lockfile data
        lockfile = {}
        
        for (pkg_name, pkg_version) in self._environments[env]:
            lockfile[pkg_name] = pkg_version
            
        # Write to file
        filename = f"{env}.lock.json" if env != "default" else "lock.json"
        
        with open(filename, "w") as f:
            json.dump(lockfile, f, indent=2)
            
        return filename
    
    def install_from_lockfile(self, lockfile_path: str) -> None:
        """
        Install packages from a lockfile.
        
        Args:
            lockfile_path: Path to the lockfile
            
        Raises:
            FileNotFoundError: If the lockfile doesn't exist
            json.JSONDecodeError: If the lockfile is invalid JSON
        """
        # Read lockfile
        with open(lockfile_path) as f:
            lockfile = json.load(f)
            
        # Install each package with the exact version
        for pkg_name, pkg_version in lockfile.items():
            # Get dependencies from registry
            dependencies = self._registry.get((pkg_name, pkg_version), [])
            
            # Install the package
            self.install_package(pkg_name, pkg_version, dependencies)
    
    def find_package(self, name: str, version_spec: str = "") -> List[Tuple[str, str]]:
        """
        Find packages in the registry matching name and version spec.
        
        Args:
            name: The name of the package to find
            version_spec: Version specification (e.g., ">=1.0,<2.0")
            
        Returns:
            List of (name, version) tuples of matching packages
        """
        matching = []
        
        for (pkg_name, pkg_version) in self._registry:
            if pkg_name == name and (not version_spec or self._version_matches(pkg_version, f"{name}{version_spec}")):
                matching.append((pkg_name, pkg_version))
                
        return matching
    
    def why(self, name: str, version: Optional[str] = None) -> str:
        """
        Explain why a package was installed.
        
        Args:
            name: The name of the package
            version: The specific version (or None for any version)
            
        Returns:
            str: Explanation of why the package was installed
            
        Raises:
            KeyError: If the package is not installed
        """
        env_history = self._installation_history[self._current_env]
        
        # Find matching packages
        for (pkg_name, pkg_version), reason in env_history.items():
            if pkg_name == name and (version is None or pkg_version == version):
                return reason
                
        if version:
            raise KeyError(f"Package {name}=={version} is not installed")
        else:
            raise KeyError(f"Package {name} is not installed")
            
    # Compatibility methods for v1 API
    def install_package_v1(self, name: str, dependencies: List[str]) -> None:
        """
        Install a package and all its dependencies (v1 API).
        
        Args:
            name: The name of the package to install
            dependencies: List of package names that this package depends on
            
        Raises:
            CircularDependencyError: If a circular dependency is detected
        """
        # Check for direct circular dependency
        if name in dependencies:
            raise CircularDependencyError(f"Package {name} depends on itself")
            
        # Check for circular dependencies with existing packages
        self._detect_circular_dependencies_v1(name, dependencies)
        
        # If already installed, just update dependencies
        if name in self._packages:
            self._packages[name].dependencies = dependencies
            # Update reverse dependencies
            for dep in dependencies:
                if dep not in self._reverse_deps:
                    self._reverse_deps[dep] = set()
                self._reverse_deps[dep].add(name)
            return
            
        # Install package
        self._packages[name] = Package(name=name, dependencies=dependencies)
        
        # Update reverse dependencies
        for dep in dependencies:
            if dep not in self._reverse_deps:
                self._reverse_deps[dep] = set()
            self._reverse_deps[dep].add(name)
            
        # Recursively install dependencies
        path = {name}  # Track path for circular dependency detection
        for dep in dependencies:
            if dep not in self._packages:
                self._install_dependency_v1(dep, path)
                
        # Also add to v2 environment
        self.install_package(name, "0.0.0", dependencies)
    
    def _detect_circular_dependencies_v1(self, name: str, dependencies: List[str]) -> None:
        """
        Check if adding these dependencies would create a circular dependency (v1 API).
        
        Args:
            name: The package name being installed
            dependencies: List of dependencies to check
            
        Raises:
            CircularDependencyError: If a circular dependency is detected
        """
        # Build dependency graph including the new package
        dep_graph = {pkg: set(self._packages[pkg].dependencies) for pkg in self._packages}
        dep_graph[name] = set(dependencies)
        
        # Check for cycles for each dependency
        for dep in dependencies:
            if dep in self._packages:
                # Check if there's a path from dep to name
                visited = set()
                to_visit = [dep]
                
                while to_visit:
                    current = to_visit.pop()
                    
                    if current == name:
                        # Found a cycle
                        raise CircularDependencyError(
                            f"Circular dependency detected: {name} depends on {dep}, which "
                            f"eventually depends back on {name}"
                        )
                    
                    if current in visited:
                        continue
                    
                    visited.add(current)
                    
                    if current in dep_graph:
                        to_visit.extend(dep_graph[current])
    
    def _install_dependency_v1(self, name: str, path: Set[str]) -> None:
        """
        Helper method to recursively install dependencies (v1 API).
        
        Args:
            name: The dependency to install
            path: Current dependency path for cycle detection
            
        Raises:
            CircularDependencyError: If a circular dependency is detected
        """
        if name in path:
            cycle = " -> ".join(path) + " -> " + name
            raise CircularDependencyError(f"Circular dependency detected: {cycle}")
            
        # Install as empty package initially
        if name not in self._packages:
            self._packages[name] = Package(name=name, dependencies=[])
            
            # Also add to v2 environment
            self.install_package(name, "0.0.0", [])
            
    def list_packages_v1(self) -> List[str]:
        """
        List all installed packages (v1 API).
        
        Returns:
            List[str]: List of installed package names
        """
        return list(self._packages.keys())
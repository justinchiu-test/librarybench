#!/usr/bin/env python3
"""
Setup script for refactoring project directories.

This script:
1. Creates a unified directory structure for a specified library
2. Copies code from persona implementations to the unified directory
3. Creates a pyproject.toml that sets up the unified library for import

Directory structure created:
- projects/{library}/unified/
  ├── unified_{library}/           # Main library code
  │   ├── common/                 # Common functionality
  │   └── {persona}/              # Persona-specific implementations
  ├── tests/
  │   └── {persona}/              # Tests for each persona
  ├── pyproject.toml
  └── setup.py
"""

import os
import shutil
import argparse
import glob
import re
import configparser
import tomli
from pathlib import Path
from collections import defaultdict


def create_unified_directory(library_name):
    """Create the unified directory structure for a library."""
    projects_dir = Path("projects")
    library_dir = projects_dir / library_name
    unified_dir = library_dir / "unified"
    
    # Create required directories if they don't exist
    os.makedirs(unified_dir, exist_ok=True)
    
    # Create the common directory for shared code
    os.makedirs(unified_dir / "common", exist_ok=True)
    os.makedirs(unified_dir / "common" / "core", exist_ok=True)
    
    # Create the tests directory
    os.makedirs(unified_dir / "tests", exist_ok=True)
    
    return unified_dir


def find_persona_dirs(library_name):
    """Find all persona directories for the specified library."""
    projects_dir = Path("projects")
    library_dir = projects_dir / library_name
    
    persona_dirs = []
    for item in os.listdir(library_dir):
        item_path = library_dir / item
        if item_path.is_dir() and item.startswith(f"{library_name}_") and item != "unified":
            # Check if the directory has any Python files (recursively)
            has_python_files = False
            for root, _, files in os.walk(item_path):
                if any(file.endswith('.py') for file in files):
                    has_python_files = True
                    break
            
            if has_python_files:
                persona_dirs.append(item_path)
            else:
                print(f"Skipping {item_path} - no Python files found")
    
    return persona_dirs


def extract_package_name(persona_dir):
    """Extract package name from pyproject.toml or setup.py in the persona directory."""
    # Try to find pyproject.toml first
    pyproject_path = persona_dir / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomli.load(f)
                
            # Try to get the name from [project] section first (modern approach)
            if "project" in pyproject_data and "name" in pyproject_data["project"]:
                return pyproject_data["project"]["name"]
                
            # Try to find in [tool.setuptools] section
            if "tool" in pyproject_data and "setuptools" in pyproject_data["tool"]:
                if "packages" in pyproject_data["tool"]["setuptools"]:
                    packages = pyproject_data["tool"]["setuptools"]["packages"]
                    if isinstance(packages, list) and len(packages) > 0:
                        return packages[0]
                    
        except Exception as e:
            print(f"Error parsing pyproject.toml in {persona_dir}: {e}")
    
    # Try with setup.py as fallback
    setup_path = persona_dir / "setup.py"
    if setup_path.exists():
        try:
            with open(setup_path, "r") as f:
                setup_content = f.read()
                
            # Look for name="package_name" pattern
            name_match = re.search(r'name\s*=\s*[\'"](.*?)[\'"]', setup_content)
            if name_match:
                return name_match.group(1)
                
            # Look for packages with explicit list
            packages_match = re.search(r'packages\s*=\s*\[\s*[\'"](.*?)[\'"]\s*\]', setup_content)
            if packages_match:
                return packages_match.group(1)
                
        except Exception as e:
            print(f"Error parsing setup.py in {persona_dir}: {e}")
    
    # Fallback: try to find a directory with __init__.py
    for item in os.listdir(persona_dir):
        item_path = persona_dir / item
        if item_path.is_dir() and not item.startswith('.') and not item.endswith('.egg-info') and item != "tests":
            if (item_path / "__init__.py").exists():
                return item
    
    # Final fallback - use directory name
    return None


def copy_persona_library(persona_dir, unified_dir, library_name):
    """Copy the library code from a persona directory to the unified structure."""
    # Extract package name from pyproject.toml or setup.py
    package_name = extract_package_name(persona_dir)
    
    # Find the main library directory
    library_dir = None
    if package_name:
        # Check if the package directory exists
        potential_dir = persona_dir / package_name
        if potential_dir.exists() and potential_dir.is_dir():
            library_dir = potential_dir
        # Check in src/package_name
        potential_dir = persona_dir / "src" / package_name
        if potential_dir.exists() and potential_dir.is_dir():
            library_dir = potential_dir
    
    # If we couldn't find the library dir by package name, try the old method
    if not library_dir:
        # Find the main library directory within the persona directory
        library_dirs = []
        
        # First, check if there's an actual Python package (directory with __init__.py)
        for item in os.listdir(persona_dir):
            item_path = persona_dir / item
            if item_path.is_dir() and not item.startswith('.') and not item.endswith('.egg-info') and item != "tests":
                # Check if it's a Python package
                if (item_path / "__init__.py").exists():
                    library_dirs.append(item_path)
        
        # If no Python package found, look for any directory with Python files
        if not library_dirs:
            for item in os.listdir(persona_dir):
                item_path = persona_dir / item
                if item_path.is_dir() and not item.startswith('.') and not item.endswith('.egg-info') and item != "tests":
                    # Check if it contains any Python files
                    has_py_files = False
                    for _, _, files in os.walk(item_path):
                        if any(file.endswith('.py') for file in files):
                            has_py_files = True
                            break
                    
                    if has_py_files:
                        library_dirs.append(item_path)
        
        if not library_dirs:
            print(f"No library directory found in {persona_dir}. Skipping.")
            return None
        
        library_dir = library_dirs[0]  # Use the first found library
        library_dir_name = library_dir.name
        # If we couldn't get a package name from pyproject.toml, use the directory name
        if not package_name:
            package_name = library_dir_name
    else:
        library_dir_name = library_dir.name
    
    persona_name = os.path.basename(persona_dir)
    persona_short_name = persona_name.replace(f"{library_name}_", "")
    
    print(f"Found library directory '{library_dir_name}' in {persona_name} (package name: {package_name})")
    
    # Create the package directory in the unified project (using original package name)
    package_dir = unified_dir / package_name
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy library files to the package directory
    for item in os.listdir(library_dir):
        src_path = library_dir / item
        dst_path = package_dir / item
        
        if os.path.isdir(src_path):
            # Use copytree for directories
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        elif os.path.isfile(src_path):
            # Use copy2 for files
            shutil.copy2(src_path, dst_path)
    
    # Check if we have a nested package structure (e.g., package_name/package_name/...)
    nested_package_dir = package_dir / package_name
    has_nested_structure = nested_package_dir.exists() and nested_package_dir.is_dir()
    if has_nested_structure:
        print(f"Detected nested package structure for {package_name}")
    
    # Copy tests to the unified tests directory
    tests_dir = persona_dir / "tests"
    if tests_dir.exists() and tests_dir.is_dir():
        unified_tests_dir = unified_dir / "tests" / persona_short_name
        os.makedirs(unified_tests_dir, exist_ok=True)
        
        # Create a top-level conftest.py if it doesn't exist yet
        unified_conftest_path = unified_dir / "conftest.py"
        if not unified_conftest_path.exists():
            with open(unified_conftest_path, "w") as f:
                f.write(f'"""Top-level test configuration for unified {library_name}."""\n\n'
                        '# Add any custom configuration for pytest here\n'
                        'pytest_plugins = []\n')
        
        # Copy test files, handling conftest.py files differently
        for item in os.listdir(tests_dir):
            src_path = tests_dir / item
            dst_path = unified_tests_dir / item
            
            if item == "conftest.py":
                # Handle conftest.py specially - check if it contains pytest_plugins and fix import paths
                with open(src_path, "r") as f:
                    conftest_content = f.read()
                
                # Remove any pytest_plugins declarations
                if "pytest_plugins" in conftest_content:
                    print(f"Found pytest_plugins in {src_path}, modifying...")
                    modified_content = re.sub(r'pytest_plugins\s*=.*?(\n|$)', '', conftest_content)
                else:
                    modified_content = conftest_content
                
                # Fix import paths based on package structure
                if has_nested_structure:
                    # For nested packages (e.g., writer_text_editor.writer_text_editor.module), 
                    # we need to fix the import paths
                    print(f"Fixing import paths in {src_path} for nested package structure")
                    # Replace direct package imports with the nested structure
                    # e.g., "package_name.module" -> "package_name.package_name.module"
                    modified_content = re.sub(
                        rf'"{package_name}\.([^"]+)"',
                        rf'"{package_name}.{package_name}.\1"', 
                        modified_content
                    )
                
                # Write the modified content
                with open(dst_path, "w") as f:
                    f.write(modified_content)
            elif os.path.isdir(src_path):
                # For directories, we need to check for nested conftest.py files
                os.makedirs(dst_path, exist_ok=True)
                
                for root, dirs, files in os.walk(src_path):
                    rel_root = os.path.relpath(root, src_path)
                    dst_root = dst_path if rel_root == "." else dst_path / rel_root
                    os.makedirs(dst_root, exist_ok=True)
                    
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(dst_root, file)
                        
                        if file == "conftest.py":
                            # Handle nested conftest.py files
                            with open(src_file, "r") as f:
                                conftest_content = f.read()
                            
                            # Remove any pytest_plugins declarations
                            if "pytest_plugins" in conftest_content:
                                print(f"Found pytest_plugins in nested conftest {src_file}, modifying...")
                                modified_content = re.sub(r'pytest_plugins\s*=.*?(\n|$)', '', conftest_content)
                            else:
                                modified_content = conftest_content
                            
                            # Fix import paths based on package structure
                            if has_nested_structure:
                                print(f"Fixing import paths in {src_file} for nested package structure")
                                # Replace direct package imports with the nested structure
                                modified_content = re.sub(
                                    rf'"{package_name}\.([^"]+)"',
                                    rf'"{package_name}.{package_name}.\1"', 
                                    modified_content
                                )
                            
                            # Write the modified content
                            with open(dst_file, "w") as f:
                                f.write(modified_content)
                        elif file.endswith('.py'):
                            # For test files, also fix imports if needed
                            if has_nested_structure:
                                with open(src_file, "r") as f:
                                    file_content = f.read()
                                
                                # Check if the file imports from the package
                                if f"import {package_name}" in file_content or f"from {package_name}" in file_content:
                                    print(f"Fixing import paths in {src_file} for nested package structure")
                                    # Fix direct imports (import package_name.module)
                                    modified_content = re.sub(
                                        rf'import {package_name}\.([^\s]+)',
                                        rf'import {package_name}.{package_name}.\1', 
                                        file_content
                                    )
                                    # Fix from imports (from package_name.module import X)
                                    modified_content = re.sub(
                                        rf'from {package_name}\.([^\s]+)',
                                        rf'from {package_name}.{package_name}.\1', 
                                        modified_content
                                    )
                                    
                                    with open(dst_file, "w") as f:
                                        f.write(modified_content)
                                else:
                                    # Just copy the file as-is
                                    shutil.copy2(src_file, dst_file)
                            else:
                                # Just copy the file as-is
                                shutil.copy2(src_file, dst_file)
                        else:
                            # Copy other files as-is
                            shutil.copy2(src_file, dst_file)
            elif os.path.isfile(src_path) and src_path.name.endswith('.py'):
                # For Python test files, also fix imports if needed
                if has_nested_structure:
                    with open(src_path, "r") as f:
                        file_content = f.read()
                    
                    # Check if the file imports from the package
                    if f"import {package_name}" in file_content or f"from {package_name}" in file_content:
                        print(f"Fixing import paths in {src_path} for nested package structure")
                        # Fix direct imports (import package_name.module)
                        modified_content = re.sub(
                            rf'import {package_name}\.([^\s]+)',
                            rf'import {package_name}.{package_name}.\1', 
                            file_content
                        )
                        # Fix from imports (from package_name.module import X)
                        modified_content = re.sub(
                            rf'from {package_name}\.([^\s]+)',
                            rf'from {package_name}.{package_name}.\1', 
                            modified_content
                        )
                        
                        with open(dst_path, "w") as f:
                            f.write(modified_content)
                    else:
                        # Just copy the file as-is
                        shutil.copy2(src_path, dst_path)
                else:
                    # Just copy the file as-is
                    shutil.copy2(src_path, dst_path)
            else:
                # Copy regular files
                shutil.copy2(src_path, dst_path)
    
    # Create a README file in the package directory
    readme_content = f"""# {package_name.capitalize()} package
    
This package is from the {persona_name} implementation.

In the unified project, this package can be used directly, or you can import common
functionality from the 'common' package.
"""
    with open(package_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    return package_name


def extract_dependencies_from_pyproject(persona_dir):
    """Extract dependencies and configurations from pyproject.toml if it exists."""
    pyproject_path = persona_dir / "pyproject.toml"
    dependencies = {
        "build-system": {},
        "project": {
            "dependencies": [],
            "optional-dependencies": defaultdict(list),
        },
        "tool": defaultdict(dict)
    }
    
    if not pyproject_path.exists():
        return dependencies
    
    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomli.load(f)
        
        # Extract build-system requirements
        if "build-system" in pyproject_data:
            dependencies["build-system"] = pyproject_data["build-system"]
        
        # Extract project dependencies
        if "project" in pyproject_data:
            if "dependencies" in pyproject_data["project"]:
                dependencies["project"]["dependencies"] = pyproject_data["project"]["dependencies"]
            
            # Extract optional dependencies (like test, dev, etc.)
            if "optional-dependencies" in pyproject_data["project"]:
                for dep_type, deps in pyproject_data["project"]["optional-dependencies"].items():
                    dependencies["project"]["optional-dependencies"][dep_type].extend(deps)
        
        # Extract tool configurations (pytest, ruff, pyright, etc.)
        if "tool" in pyproject_data:
            for tool_name, tool_config in pyproject_data["tool"].items():
                dependencies["tool"][tool_name] = tool_config
        
        print(f"Extracted dependencies from {pyproject_path}")
        return dependencies
        
    except Exception as e:
        print(f"Error parsing pyproject.toml in {persona_dir}: {e}")
        return dependencies


def merge_dependencies(all_dependencies):
    """Merge dependencies from multiple persona pyproject.toml files."""
    if not all_dependencies:
        return {
            "build-system": {
                "requires": ["setuptools>=42", "wheel"],
                "build-backend": "setuptools.build_meta"
            },
            "project": {
                "dependencies": [],
                "optional-dependencies": {}
            },
            "tool": {}
        }
    
    # Start with a default build system
    merged = {
        "build-system": {
            "requires": ["setuptools>=42", "wheel"],
            "build-backend": "setuptools.build_meta"
        },
        "project": {
            "dependencies": [],
            "optional-dependencies": defaultdict(list)
        },
        "tool": defaultdict(dict)
    }
    
    # Set of unique dependencies to avoid duplicates
    unique_deps = set()
    unique_optional_deps = defaultdict(set)
    
    for deps in all_dependencies:
        # Merge build-system requirements if any
        if deps["build-system"]:
            # Take the most comprehensive build-system requires list
            if "requires" in deps["build-system"] and len(deps["build-system"]["requires"]) > len(merged["build-system"].get("requires", [])):
                merged["build-system"]["requires"] = deps["build-system"]["requires"]
        
        # Merge project dependencies
        if "dependencies" in deps["project"]:
            for dep in deps["project"]["dependencies"]:
                # Convert list items to string format for deduplication
                dep_str = dep if isinstance(dep, str) else str(dep)
                if dep_str not in unique_deps:
                    unique_deps.add(dep_str)
                    merged["project"]["dependencies"].append(dep)
        
        # Merge optional dependencies
        for dep_type, dep_list in deps["project"]["optional-dependencies"].items():
            for dep in dep_list:
                # Convert list items to string format for deduplication
                dep_str = dep if isinstance(dep, str) else str(dep)
                if dep_str not in unique_optional_deps[dep_type]:
                    unique_optional_deps[dep_type].add(dep_str)
                    merged["project"]["optional-dependencies"][dep_type].append(dep)
        
        # Merge tool configurations
        for tool_name, tool_config in deps["tool"].items():
            # For pytest, ruff, etc. we need to preserve configuration - take the last one we see
            # Special handling for pytest: merge ini_options from different sources if needed
            if tool_name == "pytest" and "ini_options" in tool_config and "ini_options" in merged["tool"].get("pytest", {}):
                # Keep the existing ini_options and add any new ones
                for option, value in tool_config["ini_options"].items():
                    merged["tool"]["pytest"]["ini_options"][option] = value
            else:
                merged["tool"][tool_name] = tool_config
    
    # Convert defaultdicts to regular dicts for serialization
    merged["project"]["optional-dependencies"] = dict(merged["project"]["optional-dependencies"])
    merged["tool"] = dict(merged["tool"])
    
    return merged


def create_init_files(directory):
    """Create __init__.py files in all subdirectories."""
    for root, dirs, files in os.walk(directory):
        if "__init__.py" not in files:
            open(os.path.join(root, "__init__.py"), "w").close()


def create_pyproject_toml(unified_dir, library_name, package_names, merged_dependencies=None):
    """Create a pyproject.toml file for the unified library with merged dependencies."""
    
    # Create package list string for setuptools
    packages_str = '["common"'
    for package in package_names:
        packages_str += f', "{package}"'
    packages_str += ']'
    
    # Start with the basic pyproject structure
    pyproject_dict = {
        "build-system": {
            "requires": ["setuptools>=42", "wheel"],
            "build-backend": "setuptools.build_meta"
        },
        "project": {
            "name": f"unified-{library_name}",
            "version": "0.1.0",
            "description": f"Unified libraries for {library_name} with original package names preserved",
            "requires-python": ">=3.8"
        },
        "tool": {
            "setuptools": {
                "packages": eval(packages_str)  # Convert string to actual list
            }
        }
    }
    
    # Merge in dependencies if provided
    if merged_dependencies:
        # Copy build-system requirements if more comprehensive
        if "build-system" in merged_dependencies and "requires" in merged_dependencies["build-system"]:
            if len(merged_dependencies["build-system"]["requires"]) > len(pyproject_dict["build-system"]["requires"]):
                pyproject_dict["build-system"]["requires"] = merged_dependencies["build-system"]["requires"]
        
        # Copy dependencies
        if "project" in merged_dependencies:
            if "dependencies" in merged_dependencies["project"] and merged_dependencies["project"]["dependencies"]:
                pyproject_dict["project"]["dependencies"] = merged_dependencies["project"]["dependencies"]
            
            # Copy optional dependencies
            if "optional-dependencies" in merged_dependencies["project"] and merged_dependencies["project"]["optional-dependencies"]:
                pyproject_dict["project"]["optional-dependencies"] = merged_dependencies["project"]["optional-dependencies"]
        
        # Copy tool configurations (pytest, ruff, etc.)
        if "tool" in merged_dependencies and merged_dependencies["tool"]:
            for tool_name, tool_config in merged_dependencies["tool"].items():
                if tool_name != "setuptools":  # Preserve our setuptools configuration
                    pyproject_dict["tool"][tool_name] = tool_config
    
    # Convert the dictionary to TOML format
    pyproject_content = "[build-system]\n"
    requires_str = str(pyproject_dict["build-system"]["requires"]).replace("'", "\"")
    pyproject_content += f'requires = {requires_str}\n'
    pyproject_content += f'build-backend = "{pyproject_dict["build-system"]["build-backend"]}"\n\n'
    
    pyproject_content += "[project]\n"
    pyproject_content += f'name = "{pyproject_dict["project"]["name"]}"\n'
    pyproject_content += f'version = "{pyproject_dict["project"]["version"]}"\n'
    pyproject_content += f'description = "{pyproject_dict["project"]["description"]}"\n'
    pyproject_content += f'requires-python = "{pyproject_dict["project"]["requires-python"]}"\n'
    
    # Add dependencies if present
    if "dependencies" in pyproject_dict["project"]:
        deps_str = str(pyproject_dict["project"]["dependencies"]).replace("'", "\"")
        pyproject_content += f'dependencies = {deps_str}\n'
    
    # Add optional dependencies if present
    if "optional-dependencies" in pyproject_dict["project"]:
        pyproject_content += "\n[project.optional-dependencies]\n"
        for dep_type, deps in pyproject_dict["project"]["optional-dependencies"].items():
            deps_str = str(deps).replace("'", "\"")
            pyproject_content += f'{dep_type} = {deps_str}\n'
    
    # Add tool configurations
    for tool_name, tool_config in pyproject_dict["tool"].items():
        pyproject_content += f"\n[tool.{tool_name}]\n"
        
        # Handle the setuptools packages section specially
        if tool_name == "setuptools":
            pyproject_content += f'packages = {packages_str}\n'
        else:
            # Serialize other tool configurations
            nested_sections = {}
            for key, value in tool_config.items():
                if isinstance(value, dict):
                    # Collect nested dictionaries for separate sections
                    nested_sections[key] = value
                else:
                    # Handle regular key-value pairs
                    # Format values properly based on type
                    if isinstance(value, str):
                        pyproject_content += f'{key} = "{value}"\n'
                    elif isinstance(value, list):
                        value_str = str(value).replace("'", "\"")
                        pyproject_content += f'{key} = {value_str}\n'
                    else:
                        value_str = str(value)
                        pyproject_content += f'{key} = {value_str}\n'
            
            # Add nested sections after the main section
            for nested_key, nested_config in nested_sections.items():
                pyproject_content += f"\n[tool.{tool_name}.{nested_key}]\n"
                for subkey, subvalue in nested_config.items():
                    if isinstance(subvalue, str):
                        pyproject_content += f'{subkey} = "{subvalue}"\n'
                    elif isinstance(subvalue, list):
                        subvalue_str = str(subvalue).replace("'", "\"")
                        pyproject_content += f'{subkey} = {subvalue_str}\n'
                    else:
                        subvalue_str = str(subvalue)
                        pyproject_content += f'{subkey} = {subvalue_str}\n'
    
    pyproject_path = unified_dir / "pyproject.toml"
    with open(pyproject_path, "w") as f:
        f.write(pyproject_content)


def create_setup_py(unified_dir, library_name, package_names):
    """Create a setup.py file for the unified library."""
    
    # Create package list string
    packages_list = ["common"] + list(package_names)
    packages_str = str(packages_list).replace("'", '"')
    
    setup_content = f"""from setuptools import setup

setup(
    name="unified-{library_name}",
    version="0.1.0",
    description="Unified libraries for {library_name} with original package names preserved",
    packages={packages_str},
    python_requires=">=3.8",
)
"""
    
    setup_path = unified_dir / "setup.py"
    with open(setup_path, "w") as f:
        f.write(setup_content)


def create_plan_md(unified_dir, library_name, persona_dirs, package_names):
    """Create a basic PLAN.md file for the unified library."""
    plan_content = f"""# Unified {library_name.replace('_', ' ').title()} Plan

## Overview
This directory contains a unified implementation of {library_name.replace('_', ' ')} functionality
that preserves the original package names from the following persona implementations:

"""
    
    for persona_dir in persona_dirs:
        persona_name = os.path.basename(persona_dir)
        plan_content += f"- {persona_name}\n"
    
    # Create package list for documentation
    packages_list = "\n".join([f"- {package}" for package in sorted(package_names)])
    
    plan_content += f"""
## Directory Structure
```
unified/
├── common/          # Common functionality across all implementations
│   └── core/        # Core data structures and algorithms
{packages_list.replace("-", "├──")}
├── tests/
│   └── [persona]/   # Tests for each persona implementation
├── pyproject.toml
└── setup.py
```

## Implementation Plan
1. Identify common functionality across all persona implementations
2. Refactor into a shared common/core library
3. Gradually move shared functionality from original packages to common
4. Tests continue to work because original package structure is preserved
5. Eventually standardize on common interfaces across implementations

## Integration Strategy
- Original package names are preserved, so existing tests work without modification
- Common functionality is moved to the common package over time
- New code can directly use the common package
- Persona-specific extensions continue to live in their original packages
"""
    
    plan_path = unified_dir / "PLAN.md"
    with open(plan_path, "w") as f:
        f.write(plan_content)


def create_readme(unified_dir, library_name, package_names):
    """Create a README.md file for the unified library."""
    
    # Create a string listing all packages
    package_list = ", ".join([f"`{package}`" for package in sorted(package_names)])
    
    readme_content = f"""# Unified {library_name.replace('_', ' ').title()} Libraries

## Overview
This is a unified implementation of {library_name.replace('_', ' ')} functionality 
that preserves the original package names from multiple persona implementations.

The following packages are available:
- `common` - Shared functionality for all implementations
{' '.join(['- ' + f'`{package}`' for package in sorted(package_names)])}

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly:

```python
# Import from original packages (preserved for backward compatibility)
{f'import {next(iter(package_names))} # Example using first package' if package_names else '# No packages available'}

# Import from common package (for shared functionality)
from common import core
```

## Testing
Tests are preserved for each persona implementation:

```bash
cd tests
pytest
```

Record test results with:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```
"""
    
    readme_path = unified_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content)


def create_common_init(unified_dir):
    """Create the common package __init__ files."""
    
    common_dir = unified_dir / "common"
    os.makedirs(common_dir, exist_ok=True)
    
    # Create common/__init__.py
    common_init = """# Common functionality shared across packages
"""
    with open(common_dir / "__init__.py", "w") as f:
        f.write(common_init)
    
    # Create common/core/__init__.py
    core_dir = common_dir / "core"
    os.makedirs(core_dir, exist_ok=True)
    
    core_init = """# Core functionality that can be used by all packages
"""
    with open(core_dir / "__init__.py", "w") as f:
        f.write(core_init)
    
    # Create common/README.md
    readme = """# Common Package

This package contains functionality shared across all the persona-specific packages.
As the refactoring progresses, more shared code will be moved here.

## Structure:
- `core/`: Core data structures and algorithms
"""
    with open(common_dir / "README.md", "w") as f:
        f.write(readme)


def copy_instructions_from_personas(unified_dir, persona_dirs, library_name):
    """Copy INSTRUCTIONS.md from each persona directory to unified/INSTRUCTIONS_persona.md."""
    for persona_dir in persona_dirs:
        persona_name = os.path.basename(persona_dir)
        persona_short_name = persona_name.replace(f"{library_name}_", "")
        
        instructions_path = persona_dir / "INSTRUCTIONS.md"
        if instructions_path.exists():
            # Create the destination file path
            target_path = unified_dir / f"INSTRUCTIONS_{persona_short_name}.md"
            
            # Copy the INSTRUCTIONS.md
            print(f"Copying instructions from {persona_name} to {target_path}")
            shutil.copy2(instructions_path, target_path)
        else:
            print(f"No INSTRUCTIONS.md found in {persona_name}")
    
    # Copy REFACTOR.md to unified directory
    refactor_path = Path("REFACTOR.md")
    if refactor_path.exists():
        print(f"Copying REFACTOR.md to {unified_dir}")
        shutil.copy2(refactor_path, unified_dir / "REFACTOR.md")
    else:
        print("No REFACTOR.md found in root directory")


def main():
    parser = argparse.ArgumentParser(description='Setup refactoring for a library project.')
    parser.add_argument('library_name', help='Name of the library to refactor (e.g., in_memory_database)')
    args = parser.parse_args()
    
    # Normalize library name
    library_name = args.library_name.replace('-', '_')
    
    # Create unified directory structure
    unified_dir = create_unified_directory(library_name)
    print(f"Created unified directory structure at {unified_dir}")
    
    # Find persona directories
    persona_dirs = find_persona_dirs(library_name)
    if not persona_dirs:
        print(f"No persona directories found for {library_name}")
        return
    
    print(f"Found {len(persona_dirs)} persona directories for {library_name}")
    
    # Copy persona libraries to unified structure
    processed_count = 0
    package_names = set()  # Store unique package names
    all_dependencies = []  # Store dependencies from all persona dirs
    
    # First, extract dependencies from all persona directories
    for persona_dir in persona_dirs:
        print(f"Extracting dependencies from {persona_dir}...")
        dependencies = extract_dependencies_from_pyproject(persona_dir)
        all_dependencies.append(dependencies)
    
    # Merge all dependencies
    merged_dependencies = merge_dependencies(all_dependencies)
    print("Merged dependencies from all persona directories")
    
    # Now copy the libraries
    for persona_dir in persona_dirs:
        print(f"Processing {persona_dir}...")
        package_name = copy_persona_library(persona_dir, unified_dir, library_name)
        if package_name:
            package_names.add(package_name)
            processed_count += 1
    
    if processed_count == 0:
        print("No libraries were processed. Check if the persona directories have valid Python code.")
        return
    
    # Create __init__.py files in all package directories and tests
    for package_name in package_names:
        create_init_files(unified_dir / package_name)
    create_init_files(unified_dir / "tests")
    
    # Create common package structure
    create_common_init(unified_dir)
    
    # Create pyproject.toml and setup.py with merged dependencies
    create_pyproject_toml(unified_dir, library_name, package_names, merged_dependencies)
    create_setup_py(unified_dir, library_name, package_names)
    
    # Create PLAN.md and README.md
    create_plan_md(unified_dir, library_name, persona_dirs, package_names)
    create_readme(unified_dir, library_name, package_names)
    
    # Copy INSTRUCTIONS.md from each persona
    copy_instructions_from_personas(unified_dir, persona_dirs, library_name)
    
    print("Setup complete. The unified directory structure is ready for refactoring.")
    print(f"Successfully processed {processed_count} out of {len(persona_dirs)} persona directories.")
    print(f"Preserved {len(package_names)} original package names: {', '.join(sorted(package_names))}")
    print(f"Next steps:")
    print(f"1. Review the PLAN.md file")
    print(f"2. Implement shared code in the common/ package")
    print(f"3. To run tests:")
    print(f"   cd {unified_dir}")
    print(f"   pip install -e .")
    print(f"   cd tests")
    print(f"   pytest")
    print(f"4. Gradually move shared functionality to the common package")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Check projects in projects/* that have less than 2 Python packages."""

from pathlib import Path
from typing import List, Tuple


def has_python_package(directory: Path) -> bool:
    """Check if a directory contains a Python package."""
    # Check for setup.py, pyproject.toml, or requirements.txt
    package_indicators = ['setup.py', 'pyproject.toml', 'requirements.txt']
    
    for indicator in package_indicators:
        if (directory / indicator).exists():
            return True
    
    # Check for __init__.py files which indicate a package structure
    if list(directory.rglob('__init__.py')):
        return True
    
    return False


def count_python_packages(project_dir: Path) -> List[str]:
    """Count Python packages in a project directory."""
    python_packages = []
    
    # Check subdirectories within the project
    for subdir in sorted([d for d in project_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]):
        if has_python_package(subdir):
            python_packages.append(subdir.name)
    
    return python_packages


def main():
    """Find projects with less than 2 Python packages and list all projects."""
    projects_path = Path('./projects')
    
    if not projects_path.exists():
        print("Error: 'projects' directory not found!")
        return
    
    all_projects = []
    projects_with_less_than_2 = []
    
    # Iterate through each project in the projects directory
    for project_dir in sorted([d for d in projects_path.iterdir() if d.is_dir() and not d.name.startswith('.')]):
        packages = count_python_packages(project_dir)
        all_projects.append((project_dir.name, packages))
        
        if len(packages) < 2:
            projects_with_less_than_2.append((project_dir.name, packages))
    
    # Print all projects with their personas that have Python packages
    print("=== ALL PROJECTS AND THEIR PYTHON PACKAGES ===\n")
    
    for project_name, packages in all_projects:
        if packages:
            print(f"{project_name}: {len(packages)} package(s)")
            for persona in packages:
                print(f"  - {persona}")
        else:
            print(f"{project_name}: 0 packages")
    
    # Print projects with less than 2 packages
    print(f"\n=== PROJECTS WITH LESS THAN 2 PYTHON PACKAGES ({len(projects_with_less_than_2)} total) ===\n")
    
    for project_name, packages in projects_with_less_than_2:
        if packages:
            print(f"{project_name}: {len(packages)} package ({', '.join(packages)})")
        else:
            print(f"{project_name}: 0 packages")


if __name__ == "__main__":
    main()
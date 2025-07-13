#!/usr/bin/env python3
"""Check which projects have been annotated (implemented) in the current branch."""

import subprocess
from pathlib import Path
from typing import Set, Dict, List


def get_recent_python_projects() -> Set[str]:
    """Get projects with Python implementations added in recent commits."""
    try:
        # Get files added since commit ce803262
        result = subprocess.run(
            ["git", "diff", "--name-only", "ce803262..HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        
        added_files = result.stdout.strip().split('\n')
        
        # Filter for Python package indicators
        package_indicators = ['setup.py', 'pyproject.toml', 'requirements.txt', 'pytest_results.json']
        annotated_projects = set()
        
        for file_path in added_files:
            parts = file_path.split('/')
            if len(parts) >= 3 and parts[0] == 'projects':
                for indicator in package_indicators:
                    if file_path.endswith(indicator):
                        project = parts[1]
                        persona = parts[2]
                        annotated_projects.add(f"{project}/{persona}")
        
        return annotated_projects
        
    except subprocess.CalledProcessError:
        print("Error running git command")
        return set()


def check_python_package(directory: Path) -> bool:
    """Check if a directory contains a Python package."""
    package_indicators = ['setup.py', 'pyproject.toml', 'requirements.txt']
    
    for indicator in package_indicators:
        if (directory / indicator).exists():
            return True
    
    if list(directory.rglob('__init__.py')):
        return True
    
    return False


def main():
    """List annotated projects in the current branch."""
    projects_path = Path('./projects')
    
    if not projects_path.exists():
        print("Error: 'projects' directory not found!")
        return
    
    # Get recently added projects from git
    recent_projects = get_recent_python_projects()
    
    # Group by main project
    projects_by_main = {}
    for proj_persona in recent_projects:
        if '/' in proj_persona:
            main_proj, persona = proj_persona.split('/', 1)
            if main_proj not in projects_by_main:
                projects_by_main[main_proj] = []
            projects_by_main[main_proj].append(persona)
    
    print("=== PROJECTS ANNOTATED IN THIS BRANCH (claude4) ===\n")
    print(f"Total projects with new implementations: {len(projects_by_main)}\n")
    
    for project in sorted(projects_by_main.keys()):
        personas = sorted(projects_by_main[project])
        print(f"{project}: {len(personas)} persona(s)")
        for persona in personas:
            print(f"  - {persona}")
    
    print(f"\nTotal personas implemented: {len(recent_projects)}")


if __name__ == "__main__":
    main()
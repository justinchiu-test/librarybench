#!/usr/bin/env python3
"""Check which project ideas were generated in this branch and their implementation status."""

import subprocess
from pathlib import Path
from typing import Set, Dict, List, Tuple


def get_ideas_added_in_branch() -> List[str]:
    """Get idea files added in the current branch."""
    try:
        # Get files added in recent commits
        result = subprocess.run(
            ["git", "log", "--oneline", "--name-status", "-30"],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        added_ideas = []
        
        for line in lines:
            if line.startswith('A\tideas/') and line.endswith('.txt'):
                # Extract project name from ideas/project_name.txt
                file_path = line.split('\t')[1]
                project_name = Path(file_path).stem
                if project_name not in added_ideas:
                    added_ideas.append(project_name)
        
        return sorted(added_ideas)
        
    except subprocess.CalledProcessError:
        print("Error running git command")
        return []


def check_project_implementation(project_name: str) -> Tuple[bool, List[str]]:
    """Check if a project has Python implementations and return persona list."""
    project_path = Path(f'./projects/{project_name}')
    
    if not project_path.exists():
        return False, []
    
    implemented_personas = []
    
    # Check subdirectories for Python packages
    for subdir in project_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('.'):
            # Check for package indicators
            package_indicators = ['setup.py', 'pyproject.toml', 'requirements.txt']
            has_package = False
            
            for indicator in package_indicators:
                if (subdir / indicator).exists():
                    has_package = True
                    break
            
            # Also check for __init__.py files
            if not has_package and list(subdir.glob('**/__init__.py')):
                has_package = True
            
            if has_package:
                implemented_personas.append(subdir.name)
    
    return len(implemented_personas) > 0, sorted(implemented_personas)


def main():
    """Check ideas generated in this branch and their implementation status."""
    
    # Get ideas added in this branch
    added_ideas = get_ideas_added_in_branch()
    
    if not added_ideas:
        print("No new ideas found in this branch.")
        return
    
    print("=== PROJECT IDEAS GENERATED IN THIS BRANCH ===\n")
    print(f"Total ideas generated: {len(added_ideas)}\n")
    
    implemented_count = 0
    total_personas = 0
    
    for project in added_ideas:
        is_implemented, personas = check_project_implementation(project)
        
        if is_implemented:
            implemented_count += 1
            total_personas += len(personas)
            status = f"✓ IMPLEMENTED ({len(personas)} personas)"
            print(f"{project}: {status}")
            for persona in personas:
                print(f"  - {persona}")
        else:
            status = "✗ NOT IMPLEMENTED"
            print(f"{project}: {status}")
    
    print(f"\nSummary:")
    print(f"- Ideas generated: {len(added_ideas)}")
    print(f"- Ideas implemented: {implemented_count} ({implemented_count/len(added_ideas)*100:.1f}%)")
    print(f"- Total personas implemented: {total_personas}")
    
    # List unimplemented projects
    print(f"\nUnimplemented projects ({len(added_ideas) - implemented_count}):")
    for project in added_ideas:
        is_implemented, _ = check_project_implementation(project)
        if not is_implemented:
            print(f"  - {project}")


if __name__ == "__main__":
    main()
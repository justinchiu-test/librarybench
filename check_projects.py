#!/usr/bin/env python3

import os
from pathlib import Path
from collections import defaultdict

# Define base directories
BASE_DIR = Path("/home/justinchiu_cohere_com/librarybench")
IDEAS_DIR = BASE_DIR / "ideas"
PERSONAS_DIR = BASE_DIR / "personas"
PROJECTS_DIR = BASE_DIR / "projects"

def check_projects():
    # Count idea files
    idea_files = list(IDEAS_DIR.glob("*.txt"))
    print(f"Total idea files: {len(idea_files)}")
    
    # Count persona files
    persona_files = list(PERSONAS_DIR.glob("*.txt"))
    print(f"Total persona files: {len(persona_files)}")
    
    # Extract project names from idea files
    project_names = []
    for idea_file in idea_files:
        project_name = idea_file.stem  # Remove .txt extension
        project_names.append(project_name)
    
    # Check project directories
    projects_with_dirs = []
    projects_without_dirs = []
    project_persona_counts = {}
    project_instruction_counts = {}
    
    for project_name in project_names:
        project_dir = PROJECTS_DIR / project_name
        
        if project_dir.exists() and project_dir.is_dir():
            projects_with_dirs.append(project_name)
            
            # Count persona subdirectories and INSTRUCTIONS.md files
            persona_subdirs = []
            instruction_files = []
            
            for item in project_dir.iterdir():
                if item.is_dir() and item.name.startswith(f"{project_name}_"):
                    persona_subdirs.append(item.name)
                    # Check for INSTRUCTIONS.md in each persona subdirectory
                    instructions_path = item / "INSTRUCTIONS.md"
                    if instructions_path.exists():
                        instruction_files.append(item.name)
            
            project_persona_counts[project_name] = len(persona_subdirs)
            project_instruction_counts[project_name] = len(instruction_files)
        else:
            projects_without_dirs.append(project_name)
    
    # Analyze results
    print(f"\nNumber of projects with directories created: {len(projects_with_dirs)}")
    print(f"Number of projects without directories: {len(projects_without_dirs)}")
    
    # Projects with all 10 persona subdirectories
    projects_with_10_personas = [p for p, count in project_persona_counts.items() if count == 10]
    print(f"\nNumber of projects with all 10 persona subdirectories: {len(projects_with_10_personas)}")
    
    # Projects with all 10 INSTRUCTIONS.md files
    projects_with_10_instructions = [p for p, count in project_instruction_counts.items() if count == 10]
    print(f"Number of projects with all 10 INSTRUCTIONS.md files: {len(projects_with_10_instructions)}")
    
    # Incomplete projects
    print("\n=== INCOMPLETE OR MISSING PROJECTS ===")
    
    if projects_without_dirs:
        print(f"\nProjects missing directories ({len(projects_without_dirs)}):")
        for project in sorted(projects_without_dirs):
            print(f"  - {project}")
    
    incomplete_persona_projects = [(p, count) for p, count in project_persona_counts.items() if count < 10]
    if incomplete_persona_projects:
        print(f"\nProjects with incomplete persona subdirectories ({len(incomplete_persona_projects)}):")
        for project, count in sorted(incomplete_persona_projects):
            print(f"  - {project}: {count}/10 personas")
    
    incomplete_instruction_projects = [(p, count) for p, count in project_instruction_counts.items() if count < 10]
    if incomplete_instruction_projects:
        print(f"\nProjects with incomplete INSTRUCTIONS.md files ({len(incomplete_instruction_projects)}):")
        for project, count in sorted(incomplete_instruction_projects):
            print(f"  - {project}: {count}/10 INSTRUCTIONS.md files")
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"Total idea files: {len(idea_files)}")
    print(f"Total persona files: {len(persona_files)}")
    print(f"Projects with directories: {len(projects_with_dirs)}/{len(project_names)}")
    print(f"Projects with all 10 personas: {len(projects_with_10_personas)}/{len(projects_with_dirs)}")
    print(f"Projects with all 10 INSTRUCTIONS.md: {len(projects_with_10_instructions)}/{len(projects_with_dirs)}")
    print(f"Fully complete projects: {len(set(projects_with_10_personas) & set(projects_with_10_instructions))}")

if __name__ == "__main__":
    check_projects()
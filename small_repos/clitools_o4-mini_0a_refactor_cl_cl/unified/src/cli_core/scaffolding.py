"""
Project scaffolding utilities.

This module provides functionality for generating project structures and templates.
"""

import os
import shutil
import json
from typing import Dict, List, Any, Optional, Union


class ScaffoldGenerator:
    """
    Project structure and file generator.
    
    Handles template rendering and directory/file creation.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the scaffold generator.
        
        Args:
            templates_dir (str, optional): Directory containing templates.
        """
        self.templates_dir = templates_dir
    
    def create_directory(self, path: str, mode: int = 0o755) -> None:
        """
        Create a directory (and parents) if it doesn't exist.
        
        Args:
            path (str): Directory path to create.
            mode (int): Directory permission mode.
        """
        os.makedirs(path, mode=mode, exist_ok=True)
    
    def write_file(self, path: str, content: str, mode: int = 0o644) -> None:
        """
        Write content to a file.
        
        Args:
            path (str): File path to write.
            content (str): Content to write.
            mode (int): File permission mode.
        """
        with open(path, 'w') as f:
            f.write(content)
        
        # Set file permissions
        os.chmod(path, mode)
    
    def copy_template(self, template_path: str, dest_path: str) -> None:
        """
        Copy a template file to destination.
        
        Args:
            template_path (str): Template file path (relative to templates_dir).
            dest_path (str): Destination file path.
        """
        if not self.templates_dir:
            raise ValueError("Templates directory not specified")
        
        full_template_path = os.path.join(self.templates_dir, template_path)
        
        if not os.path.exists(full_template_path):
            raise FileNotFoundError(f"Template not found: {full_template_path}")
        
        if os.path.isdir(full_template_path):
            # Copy directory
            shutil.copytree(full_template_path, dest_path, dirs_exist_ok=True)
        else:
            # Copy file
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(full_template_path, dest_path)
    
    def render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Render a template string with variables.
        
        Args:
            template_content (str): Template content with placeholders.
            variables (Dict[str, Any]): Variables for template rendering.
            
        Returns:
            str: Rendered content.
        """
        # Simple template rendering with string formatting
        result = template_content
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        
        return result
    
    def render_and_write(self, template_path: str, dest_path: str, 
                        variables: Dict[str, Any]) -> None:
        """
        Render a template and write to destination.
        
        Args:
            template_path (str): Template file path (relative to templates_dir).
            dest_path (str): Destination file path.
            variables (Dict[str, Any]): Variables for template rendering.
        """
        if not self.templates_dir:
            raise ValueError("Templates directory not specified")
        
        full_template_path = os.path.join(self.templates_dir, template_path)
        
        try:
            with open(full_template_path, 'r') as f:
                template_content = f.read()
            
            rendered_content = self.render_template(template_content, variables)
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            with open(dest_path, 'w') as f:
                f.write(rendered_content)
        except (FileNotFoundError, IOError) as e:
            raise ValueError(f"Error rendering template: {e}")
    
    def generate_structure(self, structure: Dict[str, Any], base_dir: str) -> None:
        """
        Generate a directory structure from a specification.
        
        Args:
            structure (Dict[str, Any]): Structure specification.
            base_dir (str): Base directory for structure.
        """
        # Ensure base directory exists
        os.makedirs(base_dir, exist_ok=True)
        
        for name, content in structure.items():
            path = os.path.join(base_dir, name)
            
            if isinstance(content, dict):
                # It's a directory with nested content
                os.makedirs(path, exist_ok=True)
                self.generate_structure(content, path)
            else:
                # It's a file - content should be a string
                with open(path, 'w') as f:
                    f.write(str(content))


def create_project(project_name: str, template: str = "default", 
                  output_dir: str = ".", variables: Dict[str, Any] = None) -> str:
    """
    Create a new project from a template.
    
    Args:
        project_name (str): Name of the project.
        template (str): Template name.
        output_dir (str): Output directory.
        variables (Dict[str, Any]): Template variables.
        
    Returns:
        str: Path to the created project.
    """
    # Use current directory as templates source in absence of a templates directory
    scaffold = ScaffoldGenerator("templates" if os.path.exists("templates") else None)
    
    # Set up variables
    template_vars = variables or {}
    template_vars["project_name"] = project_name
    
    # Construct project directory path
    project_dir = os.path.join(output_dir, project_name)
    
    # Create basic structure
    basic_structure = {
        "__init__.py": "",
        "README.md": f"# {project_name}\n\nCreated with CLI scaffolding",
        "setup.py": f"""
from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[]
)
""",
        "requirements.txt": "",
        "tests": {
            "__init__.py": "",
            "test_basic.py": f"""
import unittest

class TestBasic(unittest.TestCase):
    def test_import(self):
        import {project_name}
        self.assertTrue(True)
"""
        }
    }
    
    # Generate structure
    scaffold.generate_structure(basic_structure, project_dir)
    
    # Return path to created project
    return project_dir
"""Utility functions for file operations."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import yaml


def ensure_directory(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path.
        
    Returns:
        Path object for the directory.
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_yaml(data: dict, file_path: Union[str, Path]) -> None:
    """Write data to a YAML file.
    
    Args:
        data: Data to write.
        file_path: Path to the file.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def read_yaml(file_path: Union[str, Path]) -> dict:
    """Read data from a YAML file.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        Data from the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def write_json(data: dict, file_path: Union[str, Path]) -> None:
    """Write data to a JSON file.
    
    Args:
        data: Data to write.
        file_path: Path to the file.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def read_json(file_path: Union[str, Path]) -> dict:
    """Read data from a JSON file.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        Data from the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def copy_file(source: Union[str, Path], destination: Union[str, Path]) -> None:
    """Copy a file from source to destination.
    
    Args:
        source: Source file path.
        destination: Destination file path.
    """
    shutil.copy2(source, destination)


def move_file(source: Union[str, Path], destination: Union[str, Path]) -> None:
    """Move a file from source to destination.
    
    Args:
        source: Source file path.
        destination: Destination file path.
    """
    shutil.move(source, destination)


def delete_file(file_path: Union[str, Path]) -> None:
    """Delete a file.
    
    Args:
        file_path: Path to the file.
    """
    Path(file_path).unlink(missing_ok=True)


def create_backup(source_dir: Union[str, Path], backup_dir: Union[str, Path]) -> Path:
    """Create a backup of a directory.
    
    Args:
        source_dir: Directory to back up.
        backup_dir: Directory to store the backup.
        
    Returns:
        Path to the created backup directory.
    """
    source_path = Path(source_dir)
    backup_path = Path(backup_dir)
    
    # Create a timestamped backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = backup_path / f"backup_{timestamp}"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all files and directories
    for item in source_path.glob('*'):
        if item.is_dir():
            shutil.copytree(item, target_dir / item.name)
        else:
            shutil.copy2(item, target_dir / item.name)
    
    return target_dir


def restore_from_backup(backup_dir: Union[str, Path], target_dir: Union[str, Path]) -> None:
    """Restore a directory from a backup.
    
    Args:
        backup_dir: Backup directory.
        target_dir: Target directory to restore to.
    """
    backup_path = Path(backup_dir)
    target_path = Path(target_dir)
    
    # Clear the target directory
    if target_path.exists():
        for item in target_path.glob('*'):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        target_path.mkdir(parents=True, exist_ok=True)
    
    # Copy all files and directories from the backup
    for item in backup_path.glob('*'):
        if item.is_dir():
            shutil.copytree(item, target_path / item.name)
        else:
            shutil.copy2(item, target_path / item.name)
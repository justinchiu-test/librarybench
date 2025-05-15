"""
Storage management for the unified incremental backup system.

This module provides functionality for storing and retrieving files and data chunks.
"""

import hashlib
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any, BinaryIO

from common.core.utils import calculate_file_hash
from common.core.chunking import ChunkingStrategy, RollingHashChunker


class StorageManager(ABC):
    """Abstract base class for storage management."""
    
    @abstractmethod
    def store_file(self, file_path: Union[str, Path]) -> Tuple[str, str]:
        """Store a file and return its hash and storage path.
        
        Args:
            file_path: Path to the file to store
            
        Returns:
            Tuple containing the file hash and storage path
        """
        pass
    
    @abstractmethod
    def retrieve_file(self, file_id: str, output_path: Union[str, Path]) -> bool:
        """Retrieve a stored file by its hash.
        
        Args:
            file_id: Hash of the file to retrieve
            output_path: Path where the file should be written
            
        Returns:
            True if the file was successfully retrieved
        """
        pass
    
    @abstractmethod
    def store_chunk(self, chunk: bytes) -> str:
        """Store a data chunk and return its hash.
        
        Args:
            chunk: Bytes to store
            
        Returns:
            Hash of the stored chunk
        """
        pass
    
    @abstractmethod
    def retrieve_chunk(self, chunk_id: str) -> bytes:
        """Retrieve a stored chunk by its hash.
        
        Args:
            chunk_id: Hash of the chunk to retrieve
            
        Returns:
            Bytes of the retrieved chunk
        """
        pass
    
    @abstractmethod
    def get_storage_size(self) -> Dict[str, int]:
        """Get statistics about storage usage.
        
        Returns:
            Dictionary containing storage statistics
        """
        pass


class FileSystemStorageManager(StorageManager):
    """Storage manager that uses the file system for storage."""
    
    def __init__(
        self, 
        storage_dir: Union[str, Path],
        chunking_strategy: Optional[ChunkingStrategy] = None
    ):
        """Initialize the file system storage manager.
        
        Args:
            storage_dir: Directory for storing files and chunks
            chunking_strategy: Optional strategy for chunking binary files
        """
        self.storage_dir = Path(storage_dir)
        self.files_dir = self.storage_dir / "files"
        self.chunks_dir = self.storage_dir / "chunks"
        self.metadata_dir = self.storage_dir / "metadata"
        
        # Create directories if they don't exist
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Set chunking strategy
        self.chunking_strategy = chunking_strategy or RollingHashChunker()
    
    def _get_path_for_hash(self, hash_value: str, base_dir: Path) -> Path:
        """Get the storage path for a hash value.
        
        Args:
            hash_value: Hash value to get path for
            base_dir: Base directory for storage
            
        Returns:
            Path where the file should be stored
        """
        # Use the first 4 chars of the hash for directory structure
        # This helps distribute files across directories
        dir1, dir2 = hash_value[:2], hash_value[2:4]
        storage_dir = base_dir / dir1 / dir2
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        return storage_dir / hash_value
    
    def store_file(self, file_path: Union[str, Path]) -> Tuple[str, str]:
        """Store a file in the files directory.
        
        Args:
            file_path: Path to the file to store
            
        Returns:
            Tuple containing the file hash and storage path
        """
        file_path = Path(file_path)
        
        # Calculate the file's hash
        file_hash = calculate_file_hash(file_path)
        
        # Determine storage path
        storage_path = self._get_path_for_hash(file_hash, self.files_dir)
        
        # Store the file if it doesn't already exist
        if not storage_path.exists():
            shutil.copy2(file_path, storage_path)
        
        return file_hash, str(storage_path)
    
    def retrieve_file(self, file_id: str, output_path: Union[str, Path]) -> bool:
        """Retrieve a file from storage by its hash.
        
        Args:
            file_id: Hash of the file to retrieve
            output_path: Path where the file should be written
            
        Returns:
            True if the file was successfully retrieved
        """
        output_path = Path(output_path)
        storage_path = self._get_path_for_hash(file_id, self.files_dir)
        
        if not storage_path.exists():
            return False
        
        # Create the parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file to the output path
        shutil.copy2(storage_path, output_path)
        
        return True
    
    def store_chunk(self, chunk: bytes) -> str:
        """Store a data chunk in the chunks directory.
        
        Args:
            chunk: Bytes to store
            
        Returns:
            Hash of the stored chunk
        """
        # Calculate the chunk's hash
        hasher = hashlib.sha256()
        hasher.update(chunk)
        chunk_hash = hasher.hexdigest()
        
        # Determine storage path
        storage_path = self._get_path_for_hash(chunk_hash, self.chunks_dir)
        
        # Store the chunk if it doesn't already exist
        if not storage_path.exists():
            with open(storage_path, 'wb') as f:
                f.write(chunk)
        
        return chunk_hash
    
    def retrieve_chunk(self, chunk_id: str) -> bytes:
        """Retrieve a chunk from storage by its hash.
        
        Args:
            chunk_id: Hash of the chunk to retrieve
            
        Returns:
            Bytes of the retrieved chunk
        """
        storage_path = self._get_path_for_hash(chunk_id, self.chunks_dir)
        
        if not storage_path.exists():
            raise FileNotFoundError(f"Chunk {chunk_id} not found")
        
        with open(storage_path, 'rb') as f:
            return f.read()
    
    def get_storage_size(self) -> Dict[str, int]:
        """Get statistics about storage usage.
        
        Returns:
            Dictionary containing storage statistics
        """
        # Calculate size of files
        files_size = sum(f.stat().st_size for f in self.files_dir.glob('**/*') if f.is_file())
        
        # Calculate size of chunks
        chunks_size = sum(f.stat().st_size for f in self.chunks_dir.glob('**/*') if f.is_file())
        
        # Count number of files and chunks
        files_count = sum(1 for _ in self.files_dir.glob('**/*') if _.is_file())
        chunks_count = sum(1 for _ in self.chunks_dir.glob('**/*') if _.is_file())
        
        return {
            "files": files_size,
            "chunks": chunks_size,
            "total": files_size + chunks_size,
            "files_count": files_count,
            "chunks_count": chunks_count
        }
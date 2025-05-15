"""
Storage module for GameVault backup engine.

This module handles the low-level storage operations for files and chunks.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from common.core.storage import StorageManager as BaseStorageManager
from common.core.chunking import ChunkingStrategy, RollingHashChunker

from gamevault.config import get_config
from gamevault.utils import compress_data, decompress_data, get_file_hash, get_file_xxhash


class StorageManager(BaseStorageManager):
    """
    Manages the physical storage of backed up files and chunks.
    
    This class handles the writing, reading, and organizing of files and chunks
    in the backup storage location, with GameVault-specific compression.
    """
    
    def __init__(self, storage_dir: Optional[Union[str, Path]] = None, chunking_strategy: Optional[ChunkingStrategy] = None):
        """
        Initialize the storage manager.
        
        Args:
            storage_dir: Directory where files will be stored. If None, uses the default from config.
            chunking_strategy: Optional chunking strategy for binary files
        """
        config = get_config()
        self.storage_dir = Path(storage_dir) if storage_dir else config.backup_dir / "storage"
        self.file_dir = self.storage_dir / "files"
        self.chunk_dir = self.storage_dir / "chunks"
        
        # Create the directory structure
        os.makedirs(self.file_dir, exist_ok=True)
        os.makedirs(self.chunk_dir, exist_ok=True)
        
        self.compression_level = config.compression_level
        self.chunking_strategy = chunking_strategy
    
    def _get_file_path(self, file_id: str) -> Path:
        """
        Get the storage path for a file.
        
        Args:
            file_id: ID (hash) of the file
            
        Returns:
            Path: Full path to the stored file
        """
        # Use first 2 characters as subdirectory to avoid too many files in one directory
        subdir = file_id[:2]
        os.makedirs(self.file_dir / subdir, exist_ok=True)
        return self.file_dir / subdir / file_id
    
    def _get_chunk_path(self, chunk_id: str) -> Path:
        """
        Get the storage path for a chunk.
        
        Args:
            chunk_id: ID (hash) of the chunk
            
        Returns:
            Path: Full path to the stored chunk
        """
        # Use first 2 characters as subdirectory to avoid too many files in one directory
        subdir = chunk_id[:2]
        os.makedirs(self.chunk_dir / subdir, exist_ok=True)
        return self.chunk_dir / subdir / chunk_id
    
    def store_file(self, file_path: Union[str, Path]) -> Tuple[str, str]:
        """
        Store a file in the backup storage with compression.
        
        Args:
            file_path: Path to the file to store
            
        Returns:
            Tuple[str, str]: File ID (hash) and storage path
        """
        file_path = Path(file_path)
        
        # Calculate file hash
        file_id = get_file_hash(file_path)
        storage_path = self._get_file_path(file_id)
        
        # Check if the file already exists in storage
        if not storage_path.exists():
            # Copy file to storage
            with open(file_path, "rb") as src_file, open(storage_path, "wb") as dest_file:
                # Read and compress data
                data = src_file.read()
                compressed_data = compress_data(data, self.compression_level)
                dest_file.write(compressed_data)
        
        return file_id, str(storage_path)
    
    def retrieve_file(self, file_id: str, output_path: Union[str, Path]) -> bool:
        """
        Retrieve a file from the backup storage and decompress it.
        
        Args:
            file_id: ID (hash) of the file to retrieve
            output_path: Path where the file should be written
            
        Returns:
            bool: True if the file was successfully retrieved
            
        Raises:
            FileNotFoundError: If the file doesn't exist in storage
        """
        storage_path = self._get_file_path(file_id)
        output_path = Path(output_path)
        
        if not storage_path.exists():
            raise FileNotFoundError(f"File with ID {file_id} not found in storage")
        
        # Create parent directories if they don't exist
        os.makedirs(output_path.parent, exist_ok=True)
        
        # Read, decompress, and write data
        with open(storage_path, "rb") as src_file, open(output_path, "wb") as dest_file:
            compressed_data = src_file.read()
            data = decompress_data(compressed_data)
            dest_file.write(data)
            
        return True
    
    def store_chunk(self, data: bytes) -> str:
        """
        Store a chunk of data in the backup storage with compression.
        
        Args:
            data: Binary data to store
            
        Returns:
            str: Chunk ID (hash)
        """
        # Calculate chunk hash
        hasher = get_file_xxhash.__globals__["xxhash"].xxh64()
        hasher.update(data)
        chunk_id = hasher.hexdigest()
        
        storage_path = self._get_chunk_path(chunk_id)
        
        # Check if the chunk already exists in storage
        if not storage_path.exists():
            # Store compressed data
            compressed_data = compress_data(data, self.compression_level)
            with open(storage_path, "wb") as f:
                f.write(compressed_data)
        
        return chunk_id
    
    def retrieve_chunk(self, chunk_id: str) -> bytes:
        """
        Retrieve a chunk of data from the backup storage and decompress it.
        
        Args:
            chunk_id: ID (hash) of the chunk to retrieve
            
        Returns:
            bytes: The chunk data
            
        Raises:
            FileNotFoundError: If the chunk doesn't exist in storage
        """
        storage_path = self._get_chunk_path(chunk_id)
        
        if not storage_path.exists():
            raise FileNotFoundError(f"Chunk with ID {chunk_id} not found in storage")
        
        # Read and decompress data
        with open(storage_path, "rb") as f:
            compressed_data = f.read()
            data = decompress_data(compressed_data)
        
        return data
    
    def file_exists(self, file_id: str) -> bool:
        """
        Check if a file exists in the backup storage.
        
        Args:
            file_id: ID (hash) of the file
            
        Returns:
            bool: True if the file exists, False otherwise
        """
        return self._get_file_path(file_id).exists()
    
    def chunk_exists(self, chunk_id: str) -> bool:
        """
        Check if a chunk exists in the backup storage.
        
        Args:
            chunk_id: ID (hash) of the chunk
            
        Returns:
            bool: True if the chunk exists, False otherwise
        """
        return self._get_chunk_path(chunk_id).exists()
    
    def get_storage_size(self) -> Dict[str, int]:
        """
        Get the total size of the backup storage.
        
        Returns:
            Dict[str, int]: Dictionary with file and chunk storage sizes
        """
        file_size = sum(f.stat().st_size for f in self.file_dir.glob("**/*") if f.is_file())
        chunk_size = sum(f.stat().st_size for f in self.chunk_dir.glob("**/*") if f.is_file())
        
        return {
            "files": file_size,
            "chunks": chunk_size,
            "total": file_size + chunk_size
        }
    
    def get_file_path_by_hash(self, file_hash: str) -> Optional[Path]:
        """
        Get the storage path for a file using its hash.
        
        Args:
            file_hash: Hash of the file to find
            
        Returns:
            Optional[Path]: Path to the stored file if found, None otherwise
        """
        file_path = self._get_file_path(file_hash)
        return file_path if file_path.exists() else None
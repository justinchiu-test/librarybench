"""
Chunking module for GameVault backup engine.

This module provides strategies for chunking binary data for efficient storage.
"""

from typing import List, Optional

# Import chunking strategies from the common library
from common.core.chunking import (
    ChunkingStrategy,
    FixedSizeChunker,
    RollingHashChunker,
    FileTypeAwareChunker
)

# Create a specialized game asset chunker based on the common FileTypeAwareChunker
class GameAssetChunker(FileTypeAwareChunker):
    """
    Specialized chunking strategy for game assets.
    
    This strategy extends the common FileTypeAwareChunker with specific
    optimizations for game-related file types.
    """
    
    def chunk_data(self, data: bytes, file_extension: Optional[str] = None) -> List[bytes]:
        """
        Chunk binary data based on the file type with game-specific optimizations.
        
        Args:
            data: Binary data to chunk
            file_extension: Extension of the file
            
        Returns:
            List[bytes]: List of chunked data
        """
        if not file_extension:
            return self.default_chunker.chunk_data(data)
        
        # Game-specific file types
        if file_extension.lower() in {".unity", ".unitypackage", ".uasset", ".upk", ".pak"}:
            # Use fixed-size chunking for Unity and Unreal engine assets
            return self.image_chunker.chunk_data(data)
        elif file_extension.lower() in {".fbx", ".max", ".blend", ".mb", ".ma"}:
            # Use content-based chunking for 3D model files (more efficient for these formats)
            return self.default_chunker.chunk_data(data)
        else:
            # Fall back to the parent implementation for other file types
            return super().chunk_data(data, file_extension)

# Re-export common chunking strategies
__all__ = ['ChunkingStrategy', 'FixedSizeChunker', 'RollingHashChunker', 'GameAssetChunker']
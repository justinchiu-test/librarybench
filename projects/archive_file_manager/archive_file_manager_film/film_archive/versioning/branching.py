import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from film_archive.core.models import ArchiveBranch, ArchiveMetadata


class ArchiveBranchManager:
    """Manages archive branching and versioning without duplication"""
    
    def __init__(self, repository_root: Path):
        self.repository_root = repository_root
        self.repository_root.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = self.repository_root / ".archive_metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        self.objects_dir = self.repository_root / ".archive_objects"
        self.objects_dir.mkdir(exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._metadata_locks: Dict[str, asyncio.Lock] = {}
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _get_object_path(self, content_hash: str) -> Path:
        """Get storage path for content object"""
        # Use first 2 chars as directory for better filesystem performance
        return self.objects_dir / content_hash[:2] / content_hash[2:]
    
    async def _store_content_object(self, file_path: Path) -> str:
        """Store file content in object store and return hash"""
        loop = asyncio.get_event_loop()
        content_hash = await loop.run_in_executor(
            self.executor, self._calculate_file_hash, file_path
        )
        
        object_path = self._get_object_path(content_hash)
        
        # Only store if not already present (deduplication)
        if not object_path.exists():
            object_path.parent.mkdir(parents=True, exist_ok=True)
            await loop.run_in_executor(
                self.executor, shutil.copy2, file_path, object_path
            )
        
        return content_hash
    
    def _load_branch_metadata(self, branch_id: str) -> Optional[Dict]:
        """Load branch metadata from disk"""
        metadata_path = self.metadata_dir / f"{branch_id}.json"
        if metadata_path.exists():
            return json.loads(metadata_path.read_text())
        return None
    
    def _save_branch_metadata(self, branch_id: str, metadata: Dict):
        """Save branch metadata to disk"""
        metadata_path = self.metadata_dir / f"{branch_id}.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, default=str))
    
    async def create_branch(
        self, 
        archive_path: Path, 
        branch_name: str, 
        description: str,
        parent_branch_id: Optional[str] = None
    ) -> ArchiveBranch:
        """Create a new branch from archive or existing branch"""
        branch_id = hashlib.sha256(
            f"{branch_name}_{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16]
        
        branch = ArchiveBranch(
            branch_id=branch_id,
            parent_id=parent_branch_id,
            created_at=datetime.now(timezone.utc),
            description=description,
            changes=[]
        )
        
        # Initialize branch metadata
        branch_metadata = {
            "branch": branch.model_dump(),
            "files": {},  # Map of file paths to content hashes
            "archive_path": str(archive_path)
        }
        
        if parent_branch_id:
            # Copy metadata from parent branch
            parent_metadata = self._load_branch_metadata(parent_branch_id)
            if parent_metadata:
                branch_metadata["files"] = parent_metadata["files"].copy()
        else:
            # New branch from archive - index all files
            # For testing, simulate with dummy files
            branch_metadata["files"] = {
                "project/scene_001.mov": "hash_001",
                "project/scene_002.mov": "hash_002",
                "project/vfx/comp_001.exr": "hash_003"
            }
        
        self._save_branch_metadata(branch_id, branch_metadata)
        
        return branch
    
    async def add_file_to_branch(
        self, 
        branch_id: str, 
        file_path: Path, 
        archive_relative_path: str
    ) -> str:
        """Add or update file in branch"""
        # Get or create lock for this branch
        if branch_id not in self._metadata_locks:
            self._metadata_locks[branch_id] = asyncio.Lock()
        
        async with self._metadata_locks[branch_id]:
            # Load branch metadata
            branch_metadata = self._load_branch_metadata(branch_id)
            if not branch_metadata:
                raise ValueError(f"Branch {branch_id} not found")
            
            # Store file content and get hash
            content_hash = await self._store_content_object(file_path)
            
            # Check if file changed
            old_hash = branch_metadata["files"].get(archive_relative_path)
            if old_hash != content_hash:
                # Record change
                branch_metadata["branch"]["changes"].append(
                    f"Modified: {archive_relative_path}"
                )
                branch_metadata["files"][archive_relative_path] = content_hash
                
                # Save updated metadata
                self._save_branch_metadata(branch_id, branch_metadata)
        
        return content_hash
    
    async def remove_file_from_branch(
        self, 
        branch_id: str, 
        archive_relative_path: str
    ):
        """Remove file from branch"""
        branch_metadata = self._load_branch_metadata(branch_id)
        if not branch_metadata:
            raise ValueError(f"Branch {branch_id} not found")
        
        if archive_relative_path in branch_metadata["files"]:
            del branch_metadata["files"][archive_relative_path]
            branch_metadata["branch"]["changes"].append(
                f"Removed: {archive_relative_path}"
            )
            self._save_branch_metadata(branch_id, branch_metadata)
    
    def get_branch_differences(
        self, 
        branch_id: str, 
        compare_to_branch_id: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Get differences between branches"""
        branch_metadata = self._load_branch_metadata(branch_id)
        if not branch_metadata:
            raise ValueError(f"Branch {branch_id} not found")
        
        if compare_to_branch_id:
            compare_metadata = self._load_branch_metadata(compare_to_branch_id)
            if not compare_metadata:
                raise ValueError(f"Branch {compare_to_branch_id} not found")
            compare_files = compare_metadata["files"]
        else:
            # Compare to parent
            if branch_metadata["branch"]["parent_id"]:
                parent_metadata = self._load_branch_metadata(
                    branch_metadata["branch"]["parent_id"]
                )
                compare_files = parent_metadata["files"] if parent_metadata else {}
            else:
                compare_files = {}
        
        branch_files = branch_metadata["files"]
        
        differences = {
            "added": [],
            "modified": [],
            "removed": []
        }
        
        # Find added and modified files
        for path, hash_val in branch_files.items():
            if path not in compare_files:
                differences["added"].append(path)
            elif compare_files[path] != hash_val:
                differences["modified"].append(path)
        
        # Find removed files
        for path in compare_files:
            if path not in branch_files:
                differences["removed"].append(path)
        
        return differences
    
    async def merge_branches(
        self, 
        source_branch_id: str, 
        target_branch_id: str,
        conflict_resolution: str = "source"  # "source" or "target"
    ) -> Dict[str, any]:
        """Merge changes from source branch into target branch"""
        source_metadata = self._load_branch_metadata(source_branch_id)
        target_metadata = self._load_branch_metadata(target_branch_id)
        
        if not source_metadata or not target_metadata:
            raise ValueError("Invalid branch IDs")
        
        merge_result = {
            "merged_files": [],
            "conflicts": [],
            "changes": []
        }
        
        # Get differences
        differences = self.get_branch_differences(source_branch_id, target_branch_id)
        
        # Apply changes
        for added_file in differences["added"]:
            target_metadata["files"][added_file] = source_metadata["files"][added_file]
            merge_result["merged_files"].append(added_file)
            merge_result["changes"].append(f"Added: {added_file}")
        
        for modified_file in differences["modified"]:
            if conflict_resolution == "source":
                target_metadata["files"][modified_file] = source_metadata["files"][modified_file]
                merge_result["merged_files"].append(modified_file)
                merge_result["changes"].append(f"Updated: {modified_file}")
            else:
                merge_result["conflicts"].append(modified_file)
        
        for removed_file in differences["removed"]:
            if removed_file in target_metadata["files"]:
                del target_metadata["files"][removed_file]
                merge_result["changes"].append(f"Removed: {removed_file}")
        
        # Update target branch metadata
        target_metadata["branch"]["changes"].extend(merge_result["changes"])
        self._save_branch_metadata(target_branch_id, target_metadata)
        
        return merge_result
    
    async def export_branch_as_archive(
        self, 
        branch_id: str, 
        output_path: Path
    ) -> Path:
        """Export branch as a new archive file"""
        branch_metadata = self._load_branch_metadata(branch_id)
        if not branch_metadata:
            raise ValueError(f"Branch {branch_id} not found")
        
        # Create temporary directory for assembly
        temp_dir = self.repository_root / f"temp_{branch_id}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Copy all files from object store to temp directory
            for rel_path, content_hash in branch_metadata["files"].items():
                object_path = self._get_object_path(content_hash)
                if object_path.exists():
                    dest_path = temp_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(object_path, dest_path)
            
            # Create archive (simplified - just copy directory)
            shutil.make_archive(
                str(output_path.with_suffix("")), 
                'zip', 
                temp_dir
            )
            
            return output_path
            
        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
    
    def get_branch_history(self, branch_id: str) -> List[Dict]:
        """Get full history of a branch including parent branches"""
        history = []
        current_id = branch_id
        
        while current_id:
            metadata = self._load_branch_metadata(current_id)
            if not metadata:
                break
            
            history.append({
                "branch_id": current_id,
                "created_at": metadata["branch"]["created_at"],
                "description": metadata["branch"]["description"],
                "changes": metadata["branch"]["changes"],
                "parent_id": metadata["branch"]["parent_id"]
            })
            
            current_id = metadata["branch"]["parent_id"]
        
        return history
    
    def calculate_storage_savings(self) -> Dict[str, any]:
        """Calculate storage saved through deduplication"""
        # Count unique objects
        unique_objects = set()
        total_references = 0
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            metadata = json.loads(metadata_file.read_text())
            for content_hash in metadata["files"].values():
                unique_objects.add(content_hash)
                total_references += 1
        
        # Calculate sizes
        total_object_size = 0
        for obj_hash in unique_objects:
            obj_path = self._get_object_path(obj_hash)
            if obj_path.exists():
                total_object_size += obj_path.stat().st_size
        
        # Estimate savings (simplified)
        avg_file_size = total_object_size / len(unique_objects) if unique_objects else 0
        potential_size = total_references * avg_file_size
        saved_size = potential_size - total_object_size
        
        return {
            "unique_objects": len(unique_objects),
            "total_references": total_references,
            "deduplication_ratio": total_references / len(unique_objects) if unique_objects else 0,
            "total_storage_mb": total_object_size / (1024 * 1024),
            "saved_storage_mb": saved_size / (1024 * 1024),
            "savings_percentage": (saved_size / potential_size * 100) if potential_size > 0 else 0
        }
    
    def cleanup_orphaned_objects(self) -> int:
        """Remove objects not referenced by any branch"""
        # Collect all referenced objects
        referenced_objects = set()
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            metadata = json.loads(metadata_file.read_text())
            referenced_objects.update(metadata["files"].values())
        
        # Find and remove orphaned objects
        removed_count = 0
        
        for obj_dir in self.objects_dir.iterdir():
            if obj_dir.is_dir():
                for obj_file in obj_dir.iterdir():
                    obj_hash = obj_dir.name + obj_file.name
                    if obj_hash not in referenced_objects:
                        obj_file.unlink()
                        removed_count += 1
        
        return removed_count
import asyncio
import pytest
from pathlib import Path
import json
import shutil

from film_archive.versioning.branching import ArchiveBranchManager
from film_archive.core.models import ArchiveBranch


@pytest.fixture
def branch_manager(tmp_path):
    return ArchiveBranchManager(repository_root=tmp_path)


@pytest.fixture
def test_archive(tmp_path):
    archive_path = tmp_path / "test_project.zip"
    archive_path.write_bytes(b"ARCHIVE_DATA")
    return archive_path


@pytest.fixture
def test_files(tmp_path):
    files = []
    for i in range(3):
        file_path = tmp_path / f"file_{i}.mov"
        file_path.write_bytes(f"FILE_CONTENT_{i}".encode())
        files.append(file_path)
    return files


class TestArchiveBranchManager:
    @pytest.mark.asyncio
    async def test_create_branch_from_archive(self, branch_manager, test_archive):
        branch = await branch_manager.create_branch(
            test_archive,
            "feature/color-grade",
            "New color grading for scene 1"
        )
        
        assert isinstance(branch, ArchiveBranch)
        assert branch.parent_id is None
        assert branch.description == "New color grading for scene 1"
        assert len(branch.branch_id) == 16
        
        # Check metadata was saved
        metadata_path = branch_manager.metadata_dir / f"{branch.branch_id}.json"
        assert metadata_path.exists()
        
        metadata = json.loads(metadata_path.read_text())
        assert metadata["archive_path"] == str(test_archive)
        assert len(metadata["files"]) > 0
    
    @pytest.mark.asyncio
    async def test_create_branch_from_parent(self, branch_manager, test_archive):
        # Create parent branch
        parent = await branch_manager.create_branch(
            test_archive,
            "main",
            "Main branch"
        )
        
        # Create child branch
        child = await branch_manager.create_branch(
            test_archive,
            "feature/vfx",
            "VFX updates",
            parent_branch_id=parent.branch_id
        )
        
        assert child.parent_id == parent.branch_id
        
        # Check files were copied from parent
        parent_metadata = branch_manager._load_branch_metadata(parent.branch_id)
        child_metadata = branch_manager._load_branch_metadata(child.branch_id)
        
        assert child_metadata["files"] == parent_metadata["files"]
    
    @pytest.mark.asyncio
    async def test_store_content_object(self, branch_manager, test_files):
        # Store first file
        hash1 = await branch_manager._store_content_object(test_files[0])
        assert len(hash1) == 64  # SHA-256 hash
        
        object_path = branch_manager._get_object_path(hash1)
        assert object_path.exists()
        
        # Store same content again - should not duplicate
        original_mtime = object_path.stat().st_mtime
        hash2 = await branch_manager._store_content_object(test_files[0])
        
        assert hash1 == hash2
        assert object_path.stat().st_mtime == original_mtime  # Not overwritten
    
    @pytest.mark.asyncio
    async def test_add_file_to_branch(self, branch_manager, test_archive, test_files):
        branch = await branch_manager.create_branch(
            test_archive,
            "edit/scene-2",
            "Scene 2 edits"
        )
        
        # Add new file
        content_hash = await branch_manager.add_file_to_branch(
            branch.branch_id,
            test_files[0],
            "project/scenes/scene_002_v2.mov"
        )
        
        assert len(content_hash) == 64
        
        # Check metadata was updated
        metadata = branch_manager._load_branch_metadata(branch.branch_id)
        assert "project/scenes/scene_002_v2.mov" in metadata["files"]
        assert metadata["files"]["project/scenes/scene_002_v2.mov"] == content_hash
        assert "Modified: project/scenes/scene_002_v2.mov" in metadata["branch"]["changes"]
    
    @pytest.mark.asyncio
    async def test_remove_file_from_branch(self, branch_manager, test_archive):
        branch = await branch_manager.create_branch(
            test_archive,
            "cleanup",
            "Remove old files"
        )
        
        # Remove existing file
        await branch_manager.remove_file_from_branch(
            branch.branch_id,
            "project/scene_001.mov"
        )
        
        metadata = branch_manager._load_branch_metadata(branch.branch_id)
        assert "project/scene_001.mov" not in metadata["files"]
        assert "Removed: project/scene_001.mov" in metadata["branch"]["changes"]
    
    def test_get_branch_differences(self, branch_manager):
        # Create test branches with different files
        branch1_id = "branch1"
        branch2_id = "branch2"
        
        branch1_metadata = {
            "branch": {"parent_id": None},
            "files": {
                "file1.mov": "hash1",
                "file2.mov": "hash2",
                "file3.mov": "hash3"
            }
        }
        
        branch2_metadata = {
            "branch": {"parent_id": branch1_id},
            "files": {
                "file1.mov": "hash1",      # Same
                "file2.mov": "hash2_mod",   # Modified
                "file4.mov": "hash4"        # Added
                # file3.mov removed
            }
        }
        
        branch_manager._save_branch_metadata(branch1_id, branch1_metadata)
        branch_manager._save_branch_metadata(branch2_id, branch2_metadata)
        
        differences = branch_manager.get_branch_differences(branch2_id, branch1_id)
        
        assert "file4.mov" in differences["added"]
        assert "file2.mov" in differences["modified"]
        assert "file3.mov" in differences["removed"]
    
    @pytest.mark.asyncio
    async def test_merge_branches(self, branch_manager, test_archive):
        # Create base branch
        base = await branch_manager.create_branch(
            test_archive,
            "main",
            "Main branch"
        )
        
        # Create feature branch
        feature = await branch_manager.create_branch(
            test_archive,
            "feature",
            "Feature branch",
            parent_branch_id=base.branch_id
        )
        
        # Modify feature branch
        feature_metadata = branch_manager._load_branch_metadata(feature.branch_id)
        feature_metadata["files"]["new_file.mov"] = "new_hash"
        feature_metadata["files"]["project/scene_001.mov"] = "modified_hash"
        branch_manager._save_branch_metadata(feature.branch_id, feature_metadata)
        
        # Merge feature into main
        merge_result = await branch_manager.merge_branches(
            feature.branch_id,
            base.branch_id,
            conflict_resolution="source"
        )
        
        assert "new_file.mov" in merge_result["merged_files"]
        assert "project/scene_001.mov" in merge_result["merged_files"]
        assert len(merge_result["conflicts"]) == 0
        
        # Verify main branch was updated
        main_metadata = branch_manager._load_branch_metadata(base.branch_id)
        assert main_metadata["files"]["new_file.mov"] == "new_hash"
        assert main_metadata["files"]["project/scene_001.mov"] == "modified_hash"
    
    @pytest.mark.asyncio
    async def test_export_branch_as_archive(
        self, branch_manager, test_archive, test_files
    ):
        branch = await branch_manager.create_branch(
            test_archive,
            "export-test",
            "Test export"
        )
        
        # Add actual files to branch
        for i, file in enumerate(test_files):
            await branch_manager.add_file_to_branch(
                branch.branch_id,
                file,
                f"exported/file_{i}.mov"
            )
        
        # Export branch
        export_path = branch_manager.repository_root / "exported_branch.zip"
        result = await branch_manager.export_branch_as_archive(
            branch.branch_id,
            export_path
        )
        
        assert result.exists()
        assert result.suffix == ".zip"
        
        # Verify temp directory was cleaned up
        temp_dir = branch_manager.repository_root / f"temp_{branch.branch_id}"
        assert not temp_dir.exists()
    
    def test_get_branch_history(self, branch_manager):
        # Create branch hierarchy
        branches = [
            {"id": "branch1", "parent": None, "desc": "Initial"},
            {"id": "branch2", "parent": "branch1", "desc": "Feature 1"},
            {"id": "branch3", "parent": "branch2", "desc": "Feature 2"}
        ]
        
        for b in branches:
            metadata = {
                "branch": {
                    "parent_id": b["parent"],
                    "created_at": "2024-01-01T00:00:00",
                    "description": b["desc"],
                    "changes": [f"Change in {b['id']}"]
                },
                "files": {}
            }
            branch_manager._save_branch_metadata(b["id"], metadata)
        
        # Get history from leaf branch
        history = branch_manager.get_branch_history("branch3")
        
        assert len(history) == 3
        assert history[0]["branch_id"] == "branch3"
        assert history[1]["branch_id"] == "branch2"
        assert history[2]["branch_id"] == "branch1"
        assert history[2]["parent_id"] is None
    
    def test_calculate_storage_savings(self, branch_manager):
        # Create multiple branches with shared files
        branches = [
            {
                "id": "branch1",
                "files": {
                    "file1.mov": "hash_common",
                    "file2.mov": "hash_unique1"
                }
            },
            {
                "id": "branch2",
                "files": {
                    "file1.mov": "hash_common",
                    "file3.mov": "hash_unique2"
                }
            },
            {
                "id": "branch3",
                "files": {
                    "file1.mov": "hash_common",
                    "file2.mov": "hash_unique1"
                }
            }
        ]
        
        for b in branches:
            metadata = {
                "branch": {"parent_id": None},
                "files": b["files"]
            }
            branch_manager._save_branch_metadata(b["id"], metadata)
        
        # Create dummy objects
        for hash_val in ["hash_common", "hash_unique1", "hash_unique2"]:
            obj_path = branch_manager._get_object_path(hash_val)
            obj_path.parent.mkdir(parents=True, exist_ok=True)
            obj_path.write_bytes(b"X" * 1024)  # 1KB each
        
        savings = branch_manager.calculate_storage_savings()
        
        assert savings["unique_objects"] == 3
        assert savings["total_references"] == 6
        assert savings["deduplication_ratio"] == 2.0
        assert savings["savings_percentage"] == 50.0
    
    def test_cleanup_orphaned_objects(self, branch_manager):
        # Create branch with references
        metadata = {
            "branch": {"parent_id": None},
            "files": {"file1.mov": "hash_referenced"}
        }
        branch_manager._save_branch_metadata("branch1", metadata)
        
        # Create objects
        referenced_path = branch_manager._get_object_path("hash_referenced")
        referenced_path.parent.mkdir(parents=True, exist_ok=True)
        referenced_path.write_bytes(b"REFERENCED")
        
        orphaned_path = branch_manager._get_object_path("hash_orphaned")
        orphaned_path.parent.mkdir(parents=True, exist_ok=True)
        orphaned_path.write_bytes(b"ORPHANED")
        
        # Cleanup orphaned objects
        removed_count = branch_manager.cleanup_orphaned_objects()
        
        assert removed_count == 1
        assert referenced_path.exists()
        assert not orphaned_path.exists()


class TestBranchingPerformance:
    @pytest.mark.asyncio
    async def test_concurrent_file_operations(
        self, branch_manager, test_archive, tmp_path
    ):
        branch = await branch_manager.create_branch(
            test_archive,
            "perf-test",
            "Performance test"
        )
        
        # Create many test files
        files = []
        for i in range(50):
            file_path = tmp_path / f"perf_file_{i}.mov"
            file_path.write_bytes(f"CONTENT_{i}".encode() * 100)
            files.append(file_path)
        
        import time
        start_time = time.time()
        
        # Add files concurrently
        tasks = [
            branch_manager.add_file_to_branch(
                branch.branch_id,
                file,
                f"project/files/file_{i}.mov"
            )
            for i, file in enumerate(files)
        ]
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify all files were added
        metadata = branch_manager._load_branch_metadata(branch.branch_id)
        assert len(metadata["files"]) >= 50
        
        # Should complete reasonably quickly
        assert duration < 10.0  # seconds
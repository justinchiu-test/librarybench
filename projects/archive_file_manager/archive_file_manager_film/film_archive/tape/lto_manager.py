import hashlib
import json
import struct
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from film_archive.core.models import TapeArchive, TapeFormat


class LTOTapeManager:
    """Manages LTO tape archive operations and LTFS formatting"""
    
    # LTO tape capacities in bytes
    TAPE_CAPACITIES = {
        TapeFormat.LTO8: 12_000_000_000_000,  # 12TB native
        TapeFormat.LTO9: 18_000_000_000_000,  # 18TB native
    }
    
    # Write speeds in MB/s
    WRITE_SPEEDS = {
        TapeFormat.LTO8: 360,  # 360 MB/s
        TapeFormat.LTO9: 400,  # 400 MB/s
    }
    
    def __init__(self, tape_staging_dir: Optional[Path] = None):
        self.staging_dir = tape_staging_dir or Path("/tmp/lto_staging")
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _create_ltfs_label(
        self, 
        tape_id: str, 
        format: TapeFormat,
        volume_name: str
    ) -> bytes:
        """Create LTFS volume label"""
        # LTFS Label structure (simplified)
        label = ET.Element("ltfslabel", version="2.4.0")
        
        # Creator
        creator = ET.SubElement(label, "creator")
        creator.text = "FilmArchiveSystem"
        
        # Format time
        formattime = ET.SubElement(label, "formattime")
        formattime.text = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Volume UUID
        volumeuuid = ET.SubElement(label, "volumeuuid")
        volumeuuid.text = hashlib.sha256(tape_id.encode()).hexdigest()
        
        # Medium info
        medium = ET.SubElement(label, "medium")
        ET.SubElement(medium, "mediuminfo").text = format.value.upper()
        
        # Blocksize
        blocksize = ET.SubElement(label, "blocksize")
        blocksize.text = "524288"  # 512KB blocks
        
        # Compression
        compression = ET.SubElement(label, "compression")
        compression.text = "true"
        
        return ET.tostring(label, encoding='utf-8', xml_declaration=True)
    
    def _create_ltfs_index(
        self, 
        tape_id: str, 
        files: List[Dict[str, any]]
    ) -> bytes:
        """Create LTFS index for tape catalog"""
        # LTFS Index structure
        index = ET.Element("ltfsindex", version="2.4.0")
        
        # Creator and time
        ET.SubElement(index, "creator").text = "FilmArchiveSystem"
        ET.SubElement(index, "updatetime").text = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Volume UUID
        ET.SubElement(index, "volumeuuid").text = hashlib.sha256(tape_id.encode()).hexdigest()
        
        # Generation number
        ET.SubElement(index, "generationnumber").text = "1"
        
        # Directory tree
        directory = ET.SubElement(index, "directory")
        ET.SubElement(directory, "name").text = "/"
        ET.SubElement(directory, "modifytime").text = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Add files to index
        for file_info in files:
            file_elem = ET.SubElement(directory, "file")
            ET.SubElement(file_elem, "name").text = file_info["name"]
            ET.SubElement(file_elem, "length").text = str(file_info["size"])
            ET.SubElement(file_elem, "modifytime").text = file_info.get(
                "modifytime", 
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            )
            
            # Extent info (simplified)
            extentinfo = ET.SubElement(file_elem, "extentinfo")
            extent = ET.SubElement(extentinfo, "extent")
            ET.SubElement(extent, "fileoffset").text = "0"
            ET.SubElement(extent, "partition").text = "a"
            ET.SubElement(extent, "startblock").text = str(file_info.get("startblock", 0))
            ET.SubElement(extent, "bytecount").text = str(file_info["size"])
        
        return ET.tostring(index, encoding='utf-8', xml_declaration=True)
    
    async def prepare_tape_archive(
        self, 
        tape_id: str, 
        format: TapeFormat,
        files_to_archive: List[Path]
    ) -> TapeArchive:
        """Prepare files for tape archiving"""
        tape_archive = TapeArchive(
            tape_id=tape_id,
            format=format,
            capacity_bytes=self.TAPE_CAPACITIES[format],
            used_bytes=0,
            span_sequence=1,
            total_spans=1
        )
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in files_to_archive if f.exists())
        
        # Check if spanning is needed
        if total_size > tape_archive.capacity_bytes:
            tape_archive.total_spans = (
                total_size // tape_archive.capacity_bytes + 1
            )
        
        tape_archive.used_bytes = min(total_size, tape_archive.capacity_bytes)
        
        return tape_archive
    
    async def write_to_tape(
        self, 
        tape_archive: TapeArchive, 
        files: List[Tuple[Path, str]],  # (file_path, archive_path)
        verify: bool = True
    ) -> Dict[str, any]:
        """Simulate writing files to LTO tape"""
        write_result = {
            "tape_id": tape_archive.tape_id,
            "written_files": [],
            "errors": [],
            "write_speed_mbps": 0,
            "duration_seconds": 0,
            "verified": False
        }
        
        # Create staging area for this tape
        tape_staging = self.staging_dir / tape_archive.tape_id
        tape_staging.mkdir(exist_ok=True)
        
        # Write LTFS label
        label_path = tape_staging / "ltfs_label.xml"
        label_data = self._create_ltfs_label(
            tape_archive.tape_id, 
            tape_archive.format,
            f"FilmArchive_{tape_archive.tape_id}"
        )
        label_path.write_bytes(label_data)
        
        # Prepare file list for index
        file_index_data = []
        current_block = 1000  # Start block for file data
        written_bytes = 0
        start_time = datetime.now(timezone.utc)
        
        for file_path, archive_path in files:
            if not file_path.exists():
                write_result["errors"].append(f"File not found: {file_path}")
                continue
            
            file_size = file_path.stat().st_size
            
            # Check if file fits on current tape
            if written_bytes + file_size > tape_archive.capacity_bytes:
                write_result["errors"].append(
                    f"File {archive_path} exceeds tape capacity"
                )
                break
            
            # Simulate writing file
            file_staging = tape_staging / archive_path
            file_staging.parent.mkdir(parents=True, exist_ok=True)
            
            # In real implementation, would write to tape device
            # Here we copy to staging area
            loop = asyncio.get_event_loop()
            file_data = await loop.run_in_executor(
                self.executor,
                file_path.read_bytes
            )
            
            # Write to staging area for verification
            await loop.run_in_executor(
                self.executor,
                file_staging.write_bytes,
                file_data
            )
            
            file_index_data.append({
                "name": archive_path,
                "size": file_size,
                "startblock": current_block,
                "modifytime": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            })
            
            write_result["written_files"].append(archive_path)
            written_bytes += file_size
            current_block += (file_size // 524288) + 1  # 512KB blocks
        
        # Write LTFS index
        index_path = tape_staging / "ltfs_index.xml"
        index_data = self._create_ltfs_index(tape_archive.tape_id, file_index_data)
        index_path.write_bytes(index_data)
        
        # Calculate write performance
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        write_result["duration_seconds"] = duration
        write_result["write_speed_mbps"] = (
            (written_bytes / (1024 * 1024)) / duration if duration > 0 else 0
        )
        
        # Verify if requested
        if verify:
            write_result["verified"] = await self._verify_tape_write(
                tape_staging, file_index_data
            )
        
        # Generate catalog
        catalog_path = await self._generate_tape_catalog(
            tape_archive, file_index_data
        )
        tape_archive.catalog_path = catalog_path
        
        # Calculate verification checksum
        tape_archive.verification_checksum = self._calculate_tape_checksum(
            tape_staging
        )
        
        return write_result
    
    async def _verify_tape_write(
        self, 
        tape_staging: Path, 
        expected_files: List[Dict]
    ) -> bool:
        """Verify tape write by reading back and comparing"""
        # In real implementation, would read from tape and verify
        # Here we check staging area
        
        for file_info in expected_files:
            file_path = tape_staging / file_info["name"]
            if not file_path.exists():
                return False
            
            # Verify size
            if file_path.stat().st_size != file_info["size"]:
                return False
        
        return True
    
    async def _generate_tape_catalog(
        self, 
        tape_archive: TapeArchive, 
        files: List[Dict]
    ) -> Path:
        """Generate offline browseable catalog"""
        catalog_path = self.staging_dir / f"{tape_archive.tape_id}_catalog.json"
        
        catalog = {
            "tape_id": tape_archive.tape_id,
            "format": tape_archive.format.value,
            "created": datetime.now(timezone.utc).isoformat(),
            "capacity_gb": tape_archive.capacity_bytes / (1024**3),
            "used_gb": tape_archive.used_bytes / (1024**3),
            "span_info": {
                "sequence": tape_archive.span_sequence,
                "total_spans": tape_archive.total_spans
            },
            "files": [
                {
                    "path": f["name"],
                    "size_mb": f["size"] / (1024**2),
                    "modified": f["modifytime"],
                    "block_start": f["startblock"]
                }
                for f in files
            ],
            "total_files": len(files),
            "checksum": tape_archive.verification_checksum
        }
        
        catalog_path.write_text(json.dumps(catalog, indent=2))
        
        return catalog_path
    
    def _calculate_tape_checksum(self, tape_staging: Path) -> str:
        """Calculate checksum for tape verification"""
        sha256_hash = hashlib.sha256()
        
        # Hash all files in order
        for file_path in sorted(tape_staging.rglob("*")):
            if file_path.is_file():
                sha256_hash.update(file_path.name.encode())
                sha256_hash.update(str(file_path.stat().st_size).encode())
        
        return sha256_hash.hexdigest()
    
    def calculate_tape_span_distribution(
        self, 
        files: List[Tuple[Path, int]], 
        format: TapeFormat
    ) -> List[List[int]]:
        """Calculate how files should be distributed across tape spans"""
        capacity = self.TAPE_CAPACITIES[format]
        spans = [[]]
        current_span_size = 0
        
        for i, (file_path, file_size) in enumerate(files):
            if file_size > capacity:
                # File spans multiple tapes
                # Add to current span if it has room
                if current_span_size == 0:
                    spans[-1].append(i)
                else:
                    spans.append([i])
                # Calculate how many additional spans needed
                remaining_size = file_size - capacity
                while remaining_size > 0:
                    spans.append([i])  # Same file continues on next tape
                    remaining_size -= capacity
                current_span_size = 0
            elif current_span_size + file_size > capacity:
                # Start new span
                spans.append([i])
                current_span_size = file_size
            else:
                spans[-1].append(i)
                current_span_size += file_size
        
        return spans
    
    async def restore_from_tape(
        self, 
        tape_id: str, 
        file_patterns: List[str],
        restore_dir: Path
    ) -> Dict[str, any]:
        """Restore files from tape based on patterns"""
        restore_result = {
            "tape_id": tape_id,
            "restored_files": [],
            "errors": [],
            "duration_seconds": 0
        }
        
        start_time = datetime.now(timezone.utc)
        
        # Load catalog
        catalog_path = self.staging_dir / f"{tape_id}_catalog.json"
        if not catalog_path.exists():
            restore_result["errors"].append("Tape catalog not found")
            return restore_result
        
        catalog = json.loads(catalog_path.read_text())
        
        # Find matching files
        import fnmatch
        matching_files = []
        
        for file_info in catalog["files"]:
            for pattern in file_patterns:
                if fnmatch.fnmatch(file_info["path"], pattern):
                    matching_files.append(file_info)
                    break
        
        # Simulate restore
        restore_dir.mkdir(parents=True, exist_ok=True)
        
        for file_info in matching_files:
            # In real implementation, would read from tape
            # Here we simulate with dummy data
            restore_path = restore_dir / file_info["path"]
            restore_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create dummy restored file
            restore_path.write_bytes(b"RESTORED_FILE_DATA")
            restore_result["restored_files"].append(file_info["path"])
        
        end_time = datetime.now(timezone.utc)
        restore_result["duration_seconds"] = (
            end_time - start_time
        ).total_seconds()
        
        return restore_result
    
    def estimate_tape_requirements(
        self, 
        total_size_bytes: int, 
        format: TapeFormat
    ) -> Dict[str, any]:
        """Estimate number of tapes needed for archive"""
        capacity = self.TAPE_CAPACITIES[format]
        write_speed = self.WRITE_SPEEDS[format]
        
        # Account for LTFS overhead (approximately 3%)
        ltfs_overhead = 0.03
        effective_capacity = capacity * (1 - ltfs_overhead)
        
        # Calculate number of tapes (round up)
        tapes_needed = int((total_size_bytes + effective_capacity - 1) / effective_capacity)
        
        # Estimate write time
        write_time_hours = (total_size_bytes / (write_speed * 1024 * 1024)) / 3600
        
        # Add time for tape changes and verification
        total_time_hours = write_time_hours * 1.5
        
        return {
            "format": format.value,
            "tapes_needed": tapes_needed,
            "capacity_per_tape_tb": capacity / (1000**4),  # TB not TiB
            "total_capacity_needed_tb": total_size_bytes / (1024**4),
            "estimated_write_time_hours": write_time_hours,
            "total_time_with_verification_hours": total_time_hours,
            "cost_estimate_usd": tapes_needed * 150  # Approximate LTO-8 tape cost
        }
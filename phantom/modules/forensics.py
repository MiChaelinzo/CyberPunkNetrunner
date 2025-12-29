#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Forensics Module

Digital forensics capabilities including memory analysis,
disk imaging, file carving, and timeline reconstruction.
"""

import os
import hashlib
import struct
import mimetypes
from typing import Dict, Any, List, Optional, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class FileMetadata:
    """File metadata container"""
    path: str
    size: int
    created: str
    modified: str
    accessed: str
    permissions: str
    owner: str
    md5: str = ""
    sha256: str = ""
    mime_type: str = ""


@dataclass
class ForensicArtifact:
    """Forensic artifact container"""
    artifact_type: str
    source: str
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)
    relevance: str = "unknown"


class HashCalculator:
    """Calculate cryptographic hashes"""
    
    @staticmethod
    def md5(filepath: str) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def sha256(filepath: str) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def sha1(filepath: str) -> str:
        """Calculate SHA1 hash of file"""
        hash_sha1 = hashlib.sha1()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_sha1.update(chunk)
            return hash_sha1.hexdigest()
        except Exception:
            return ""


class MetadataExtractor:
    """Extract metadata from files"""
    
    def extract(self, filepath: str) -> FileMetadata:
        """Extract metadata from a file"""
        try:
            stat = os.stat(filepath)
            
            return FileMetadata(
                path=filepath,
                size=stat.st_size,
                created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                accessed=datetime.fromtimestamp(stat.st_atime).isoformat(),
                permissions=oct(stat.st_mode)[-3:],
                owner=str(stat.st_uid),
                md5=HashCalculator.md5(filepath),
                sha256=HashCalculator.sha256(filepath),
                mime_type=mimetypes.guess_type(filepath)[0] or "unknown"
            )
        except Exception as e:
            return FileMetadata(
                path=filepath,
                size=0,
                created="",
                modified="",
                accessed="",
                permissions="",
                owner="",
            )
    
    def extract_directory(self, dirpath: str) -> List[FileMetadata]:
        """Extract metadata from all files in directory"""
        metadata_list = []
        
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                filepath = os.path.join(root, file)
                metadata_list.append(self.extract(filepath))
        
        return metadata_list


class FileCarver:
    """Carve files from raw data"""
    
    FILE_SIGNATURES = {
        'jpeg': {
            'header': b'\xff\xd8\xff',
            'footer': b'\xff\xd9',
            'extension': '.jpg'
        },
        'png': {
            'header': b'\x89PNG\r\n\x1a\n',
            'footer': b'\x00\x00\x00\x00IEND\xaeB`\x82',
            'extension': '.png'
        },
        'pdf': {
            'header': b'%PDF',
            'footer': b'%%EOF',
            'extension': '.pdf'
        },
        'zip': {
            'header': b'PK\x03\x04',
            'footer': b'PK\x05\x06',
            'extension': '.zip'
        },
        'exe': {
            'header': b'MZ',
            'footer': None,
            'extension': '.exe'
        },
        'elf': {
            'header': b'\x7fELF',
            'footer': None,
            'extension': ''
        }
    }
    
    def __init__(self, output_dir: str = "/tmp/carved"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def carve(self, source_path: str, file_types: Optional[List[str]] = None) -> List[str]:
        """Carve files from source"""
        file_types = file_types or list(self.FILE_SIGNATURES.keys())
        carved_files = []
        
        try:
            with open(source_path, 'rb') as f:
                data = f.read()
            
            for file_type in file_types:
                if file_type not in self.FILE_SIGNATURES:
                    continue
                
                sig = self.FILE_SIGNATURES[file_type]
                header = sig['header']
                footer = sig['footer']
                ext = sig['extension']
                
                # Find all occurrences of header
                start = 0
                file_count = 0
                
                while True:
                    pos = data.find(header, start)
                    if pos == -1:
                        break
                    
                    # Find footer or use max size
                    if footer:
                        end = data.find(footer, pos + len(header))
                        if end == -1:
                            end = min(pos + 10*1024*1024, len(data))  # 10MB max
                        else:
                            end += len(footer)
                    else:
                        end = min(pos + 10*1024*1024, len(data))
                    
                    # Extract file
                    carved_data = data[pos:end]
                    output_path = os.path.join(
                        self.output_dir,
                        f"{file_type}_{file_count}{ext}"
                    )
                    
                    with open(output_path, 'wb') as out:
                        out.write(carved_data)
                    
                    carved_files.append(output_path)
                    file_count += 1
                    start = end
            
        except Exception as e:
            print(f"[-] Carving error: {e}")
        
        return carved_files


class TimelineBuilder:
    """Build forensic timeline from artifacts"""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
    
    def add_event(self, timestamp: str, event_type: str, description: str, source: str):
        """Add event to timeline"""
        self.events.append({
            'timestamp': timestamp,
            'type': event_type,
            'description': description,
            'source': source
        })
    
    def build_from_directory(self, dirpath: str) -> List[Dict[str, Any]]:
        """Build timeline from directory contents"""
        extractor = MetadataExtractor()
        files = extractor.extract_directory(dirpath)
        
        for file_meta in files:
            # Add creation event
            if file_meta.created:
                self.add_event(
                    file_meta.created,
                    'file_created',
                    f"File created: {file_meta.path}",
                    file_meta.path
                )
            
            # Add modification event
            if file_meta.modified and file_meta.modified != file_meta.created:
                self.add_event(
                    file_meta.modified,
                    'file_modified',
                    f"File modified: {file_meta.path}",
                    file_meta.path
                )
        
        # Sort by timestamp
        self.events.sort(key=lambda x: x['timestamp'])
        return self.events
    
    def export_csv(self, output_path: str):
        """Export timeline to CSV"""
        import csv
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'type', 'description', 'source'])
            writer.writeheader()
            writer.writerows(self.events)
    
    def export_json(self, output_path: str):
        """Export timeline to JSON"""
        import json
        
        with open(output_path, 'w') as f:
            json.dump(self.events, f, indent=2)


class DiskImager:
    """Create forensic disk images"""
    
    def create_image(self, source: str, destination: str, block_size: int = 4096) -> Dict[str, Any]:
        """Create disk image using dd"""
        import subprocess
        import time
        
        start_time = time.time()
        
        try:
            # Use dd to create image
            result = subprocess.run(
                [
                    'dd',
                    f'if={source}',
                    f'of={destination}',
                    f'bs={block_size}',
                    'status=progress'
                ],
                capture_output=True,
                text=True
            )
            
            elapsed = time.time() - start_time
            
            # Calculate hash of image
            image_hash = HashCalculator.md5(destination)
            
            return {
                'success': result.returncode == 0,
                'source': source,
                'destination': destination,
                'elapsed_time': elapsed,
                'md5': image_hash,
                'stderr': result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_image(self, source: str, image: str) -> bool:
        """Verify image integrity"""
        source_hash = HashCalculator.md5(source)
        image_hash = HashCalculator.md5(image)
        return source_hash == image_hash


class ForensicsModule:
    """
    Master Forensics Module
    
    Provides:
    - Hash calculation
    - Metadata extraction
    - File carving
    - Timeline building
    - Disk imaging
    """
    
    def __init__(self):
        self.hash_calc = HashCalculator()
        self.metadata_extractor = MetadataExtractor()
        self.file_carver = FileCarver()
        self.timeline_builder = TimelineBuilder()
        self.disk_imager = DiskImager()
        self.artifacts: List[ForensicArtifact] = []
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Perform comprehensive file analysis"""
        metadata = self.metadata_extractor.extract(filepath)
        
        return {
            'metadata': vars(metadata),
            'hashes': {
                'md5': HashCalculator.md5(filepath),
                'sha1': HashCalculator.sha1(filepath),
                'sha256': HashCalculator.sha256(filepath)
            }
        }
    
    def analyze_directory(self, dirpath: str) -> Dict[str, Any]:
        """Analyze all files in directory"""
        files = self.metadata_extractor.extract_directory(dirpath)
        timeline = self.timeline_builder.build_from_directory(dirpath)
        
        return {
            'total_files': len(files),
            'files': [vars(f) for f in files],
            'timeline_events': len(timeline),
            'timeline': timeline
        }
    
    def carve_files(self, source: str, output_dir: str = "/tmp/carved") -> List[str]:
        """Carve files from source"""
        self.file_carver.output_dir = output_dir
        return self.file_carver.carve(source)
    
    def create_disk_image(self, source: str, destination: str) -> Dict[str, Any]:
        """Create forensic disk image"""
        return self.disk_imager.create_image(source, destination)
    
    def build_timeline(self, dirpath: str, output_format: str = "json") -> str:
        """Build and export timeline"""
        self.timeline_builder.events = []
        self.timeline_builder.build_from_directory(dirpath)
        
        output_path = f"/tmp/timeline.{output_format}"
        
        if output_format == "json":
            self.timeline_builder.export_json(output_path)
        elif output_format == "csv":
            self.timeline_builder.export_csv(output_path)
        
        return output_path

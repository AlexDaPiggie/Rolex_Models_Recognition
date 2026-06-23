import csv 
from dataclasses import dataclass, asdict
from pathlib import Path

MANIFEST_COMPONENTS = [
    'image_id', 
    'label', 
    'source_name', 
    'listing_title', 
    'listing_url',
    'image_url',
    'local_path', 
    'downloaded_at', 
    'file_size_bytes', 
    'width', 
    'height', 
    'sha256', 
    'perceptual_hash', 
    'status', 
    'rejection_reason'
]

@dataclass(frozen=True)
class ManifestRecord():
    image_id: str
    label: str
    source_name: str
    listing_title: str
    listing_url: str
    image_url: str
    local_path: str
    downloaded_at: str
    file_size_bytes: int
    width: int
    height: int
    sha256: str
    perceptual_hash: str
    status: str
    rejection_reason: str = ''

def append_record (manifest_path: Path, record: ManifestRecord):
    manifest_path.parent.mkdir (parents = True, exist_ok=True)
    file_exists = manifest_path.exists()
    with manifest_path.open ('a', encoding = 'utf-8', newline = '') as handle: 
        writer = csv.DictWriter (handle, fieldnames=MANIFEST_COMPONENTS)
        if not file_exists: 
            writer.writeheader() 
        writer.writerow(asdict(record))
    return None

def read_manifest (manifest_path: Path): 
    if not manifest_path.exists(): 
        return []
    with manifest_path.open ('r', encoding='utf-8', newline= '') as handle:
        reader = csv.DictReader(handle)
        records = []
        for row in reader: 
            row['file_size_bytes'] = int(row['file_size_bytes'])
            row['width'] = int (row['width'])
            row['height'] = int (row['height'])
            records.append (ManifestRecord(**row))
    return records
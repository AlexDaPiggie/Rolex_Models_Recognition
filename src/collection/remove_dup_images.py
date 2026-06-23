import argparse
import csv
import shutil
from dataclasses import asdict, replace 
from pathlib import Path
from src.collection.manifest import ManifestRecord, MANIFEST_COMPONENTS, read_manifest

def hamming_distance(left: str, right: str):
    return bin (int(left, 16) ^ int(right, 16)).count ('1')

def mark_duplicates(
    records: list[ManifestRecord],
    phash_threshold = 4,
):
    seen_sha256 = set()
    seen_percentual_hash = []
    updated_records = []
    
    for record in records: 
        if record.status != 'downloaded':
            updated_records.append (record)
            continue
        exact_duplicate = bool (record.sha256 and record.sha256 in seen_sha256)
        near_duplicate = bool (
            record.perceptual_hash and any (
                hamming_distance(record.perceptual_hash, existing_hash) <= phash_threshold
                for existing_hash in seen_percentual_hash
            )
        )

        if exact_duplicate or near_duplicate:
            updated_records.append (
                replace(record, status = 'duplicate', rejection_reason = 'duplicate_image')
            )
            continue

        updated_records.append(record)
        if record.sha256:
            seen_sha256.add (record.sha256)
        if record.perceptual_hash:
            seen_percentual_hash.append(record.perceptual_hash)
    return updated_records

def write_manifest(path: Path, records: list[ManifestRecord]):
    path.parent.mkdir (parents = True, exist_ok = True)
    with path.open('w', newline = '', encoding = 'utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COMPONENTS)
        writer.writeheader()
        for record in records: 
            writer.writerow(asdict (record)) 

def move_duplicate_files (
    records: list[ManifestRecord],
    duplicate_root = Path('data/duplicates')
):
    updated_records = []
    for record in records: 
        if record.status != 'duplicate': 
            updated_records.append (record)
            continue
        source_path = Path (record.local_path)
        if not source_path.exists(): 
            updated_records.append (record)
            continue
        target_path = duplicate_root / record.label / source_path.name
        target_path.parent.mkdir (parents = True, exist_ok=True)
        shutil.move (str(source_path), str(target_path))
        updated_records.append (replace (record, local_path = str (target_path)))
    return updated_records
        
def parse_args(): 
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type = Path, default=Path('data/manifests/images.csv'))
    parser.add_argument('--phash-threshold', type = int, default = 4)
    parser.add_argument('--move-files', action = 'store_true')
    parser.add_argument('--duplicate-root', type = Path, default=Path('data/duplicates'))
    return parser.parse_args()

def main(): 
    args = parse_args()
    records = read_manifest(args.manifest)
    updated_records = mark_duplicates(records, phash_threshold=args.phash_threshold)
    if args.move_files: 
        updated_records = move_duplicate_files(
            updated_records,
            duplicate_root=args.duplicate_root
        )
    write_manifest(args.manifest, updated_records)
    duplicate_count = sum (1 for record in updated_records if record.status == 'duplicate')
    print (f'Marked {duplicate_count} duplicate images') 


if __name__ == "__main__": 
    main()

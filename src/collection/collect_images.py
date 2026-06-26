import argparse
import uuid
from datetime import datetime, timezone, UTC
from pathlib import Path 
import requests 
from src.collection.manifest import ManifestRecord, append_record
from src.collection.sources import get_source 
from src.collection.validate_images import validate_image 
from src.collection.sources import get_source, VALID_LABELS

def download_image(image_url: str, output_path: Path, timeout_seconds = 30): 
    '''
    This function is to download the image from the image_url and save it to the output path directory
    '''
    response = requests.get (
        image_url, 
        timeout=timeout_seconds,
        headers={'User-Agent': 'Webscraper/0.1'}, 
    )

    response.raise_for_status() 
    output_path.parent.mkdir(parents = True, exist_ok=True)
    output_path.write_bytes(response.content)

def collect_images (
    source_name: str, 
    label: str, 
    limit: int, 
    output_root: Path, 
    manifest_path: Path
): 
    
    '''
    This image simply calles collect from sources.py to scrape the images from the website and save it in candidates. It creates unique id for each image to avoid repetition, and make sure the input images have the right size. Eventually, it download the approaved images to the output path and document that to maifest record.
    '''
    source = get_source(source_name)
    candidates = source.collect (label = label, limit = limit)
    count = 0 

    for candidate in candidates:
        image_id = uuid.uuid4().hex
        local_path = output_root / label / f"{image_id}.jpg"
        try: 
            download_image (candidate.image_url, local_path)
            validation = validate_image(local_path)
            status = "downloaded" if validation.is_valid else "invalid"
            rejection_reason = validation.rejection_reason

        except requests.RequestException as exc:
            validation = None
            status = 'invalid'
            rejection_reason = f"download_error: {exc.__class__.__name__}"
        
        record = ManifestRecord(
            image_id=image_id,
            label=label,
            source_name=source_name,
            listing_title=candidate.listing_title,
            listing_url=candidate.listing_url,
            image_url=candidate.image_url,
            local_path=str(local_path),
            downloaded_at=datetime.now(UTC).isoformat(),
            file_size_bytes=validation.file_size_bytes if validation else 0,
            width=validation.width if validation else 0,
            height=validation.height if validation else 0,
            sha256=validation.sha256 if validation else "",
            perceptual_hash = validation.perceptual_hash if validation else "",
            status = status, 
            rejection_reason = rejection_reason,
        )
        
        append_record (manifest_path, record)
        count += 1

    return count

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, choices = ['swisswatchexpo'])
    parser.add_argument('--label', required=True, choices = sorted(VALID_LABELS) + ['all'])
    parser.add_argument('--limit', type = int, default=100000)
    parser.add_argument('--output-root', type = Path, default=Path('data/raw_incoming'))
    parser.add_argument('--manifest', type = Path, default = Path('data/manifests/images.csv'))
    return parser.parse_args()

def main(): 
    args = parse_args()
    labels = sorted(VALID_LABELS) if args.label == 'all' else [args.label]
    total = 0
    for label in labels:
        count = collect_images(
            args.source,
            label,
            args.limit,
            args.output_root,
            args.manifest,
        )
        total += count
        print (f'Recorded {count} candidate images for {label}')
    print (f'Recorded {total} total candidate images')
    
if __name__ == "__main__": 
    main()
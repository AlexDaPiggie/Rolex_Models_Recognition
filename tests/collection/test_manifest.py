from pathlib import Path
from src.collection.manifest import ManifestRecord, append_record, read_manifest

def test_manifest (tmp_path: Path): 
    manifest_path = tmp_path / 'images.csv'
    record = ManifestRecord (
        image_id = "abcxyz123", 
        label = 'datejust', 
        source_name = 'watchfinder', 
        listing_title = 'Rolex Datejust 36', 
        listing_url = 'https://abc.com/listing', 
        image_url = 'https://example.com/image.jpb',
        local_path = 'data/raw_images/datejust/abc12.jpg',
        downloaded_at = '2026-06-19T10:00:00Z',
        file_size_bytes = 1234,
        width = 800,
        height = 600,
        sha256 = 'sh', 
        perceptual_hash = 'phash', 
        status = 'downloaded', 
        rejection_reason = '', 
    )

    append_record (manifest_path, record)

    records = read_manifest(manifest_path)
    assert len(records) == 1
    assert records[0].label == 'datejust'
    assert records[0].source_name == 'watchfinder'
    assert records[0].status == 'downloaded'
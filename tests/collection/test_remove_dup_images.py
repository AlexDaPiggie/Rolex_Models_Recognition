from src.collection.remove_dup_images import hamming_distance, main, mark_duplicates, move_duplicate_files, write_manifest
from src.collection.manifest import read_manifest
from src.collection.manifest import ManifestRecord
from pathlib import Path

def make_record (
    image_id: str,
    sha256: str,
    perceptual_hash: str,
    status = "downloaded",
): 
    '''
    Avoid having to intialize manifestrecord all the time
    '''
    return ManifestRecord(
        image_id = image_id,
        label = 'submariner',
        source_name = 'watchfinder',
        listing_title = 'Rolex Submariner',
        listing_url = 'https://example.com/listing', 
        image_url = 'https://example.com/image.jpg', 
        local_path = f'data/raw_incoming/submariner/{image_id}.jpg',
        downloaded_at = "2026-06-20T10:00:00Z",
        file_size_bytes=1234,
        width=500,
        height=500,
        sha256=sha256,
        perceptual_hash=perceptual_hash,
        status=status,
        rejection_reason=''
    )

def test_hamming_distance (): 
    assert hamming_distance('0', '0') == 0
    assert hamming_distance('0', 'f') == 4
    assert hamming_distance('ff', '0f') == 4

def test_mark_duplicates_same_sha(): 
    records = [
        make_record('first', sha256='same', perceptual_hash='0000000000000000'),
        make_record('second', sha256='same', perceptual_hash='1111111111111111')
    ]
    updated = mark_duplicates(records)
    assert updated[0].status == 'downloaded'
    assert updated[0].rejection_reason == ''
    assert updated[1].status == 'duplicate'
    assert updated[1].rejection_reason == 'duplicate_image'

def test_mark_duplicates_clost_perceptual_hash(): 
    records = [
        make_record('first', sha256='same1', perceptual_hash='0000000000000000'),
        make_record('second', sha256='same2', perceptual_hash='0000000000000001'),
    ]
    updated = mark_duplicates(records)
    assert updated[0].status == 'downloaded'
    assert updated[0].rejection_reason == ''
    assert updated[1].status == 'duplicate'
    assert updated[1].rejection_reason == 'duplicate_image'

def test_mark_ignore_undownloaded_records():
    records = [
        make_record('first', sha256='same', perceptual_hash='0000000000000000', status = 'invalid'),
        make_record('second', sha256='same', perceptual_hash='0000000000000000', status = 'downloaded'),
    ]
    updated = mark_duplicates(records)
    assert updated[0].status == 'invalid'
    assert updated[1].status == 'downloaded'

def test_move_duplicates_files(tmp_path: Path): 
    raw_root = tmp_path / 'raw_incoming' / 'submariner'
    raw_root.mkdir (parents = True)
    duplicate_file = raw_root / 'duplicate.jpg'
    unique_file = raw_root / 'unique.jpg'
    duplicate_file.write_bytes (b"duplicate")
    unique_file.write_bytes (b"unique")

    records = [
        make_record (
            'duplicate',
            sha256='duplicate',
            perceptual_hash='0000000000000000',
            status = 'duplicate',
        ),
        make_record (
            'unique',
            sha256='unique',
            perceptual_hash='1111111111111111',
            status = 'downloaded'
        )
    ]

    records[0] = records[0].__class__(**{**records[0].__dict__, 'local_path': str(duplicate_file)})
    records[1] = records[1].__class__(**{**records[1].__dict__, 'local_path': str(unique_file)})
    updated  = move_duplicate_files(records, duplicate_root=tmp_path / 'duplicates')
    moved_path = Path (updated[0].local_path)
    assert moved_path.exists()
    assert moved_path.parent == tmp_path / 'duplicates' / 'submariner'
    assert not duplicate_file.exists()
    assert unique_file.exists()
    assert updated[1].local_path == str(unique_file)
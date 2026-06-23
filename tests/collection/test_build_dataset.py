from pathlib import Path
import pytest
import json
from src.collection.build_dataset import build_dataset, main
from src.collection.sources import VALID_LABELS

def make_images (root: Path, label: str, count: int): 
    class_dir = root / label
    class_dir.mkdir (parents = True, exist_ok=True)

    #write files like datejust_00, datejust_01,...
    for index in range (count): 
        (class_dir / f"{label}_{index:02d}.jpg").write_bytes(
            f"{label}-{index}".encode ('utf-8')
        )

def list_names (path: Path): 
    return sorted (item.name for item in path.glob ('*.jpg'))

def test_build_dataset_rejects(tmp_path):
    raw_incoming = tmp_path / 'raw_incoming'
    output = tmp_path / 'processed'
    make_images(raw_incoming, 'speedmaster', 10)
    with pytest.raises(
        ValueError,
        match = 'Unknown input label'
    ):
        build_dataset(
            input_root=raw_incoming,
            output_root=output,
        )

def test_build_dataset_splits(tmp_path):
    raw_incoming = tmp_path / 'raw_incoming'
    output = tmp_path / 'processed'
    make_images (raw_incoming, 'datejust', 10)
    make_images (raw_incoming, 'submariner', 10)
    make_images (raw_incoming, 'gmt_master', 10)
    make_images (raw_incoming, 'yacht_master', 10)

    build_dataset (
        input_root=raw_incoming,
        output_root=output,
        seed = 42,
    )

    for label in ('datejust', 'submariner', 'gmt_master', 'yacht_master'):
        assert len(list_names (output / 'train' / label)) == 7
        assert len(list_names (output / 'val' / label)) == 1
        assert len(list_names (output / 'test' / label)) == 2

    assert list_names(output / 'train' / 'datejust')
    assert (output / 'class_mapping.json').exists()

def test_build_dataset_merge_datejusts(tmp_path):
    raw_incoming = tmp_path / 'raw_incoming'
    output = tmp_path / 'processed'
    make_images(raw_incoming, 'datejust', 10)
    make_images(raw_incoming, 'datejust41', 10)
    make_images(raw_incoming, 'submariner', 10)

    build_dataset(
        input_root=raw_incoming,
        output_root=output,
        seed=42,
    )

    assert len(list_names(output / 'train' / 'datejust')) == 14
    assert len(list_names(output / 'val' / 'datejust')) == 3
    assert len(list_names(output / 'test' / 'datejust')) == 3
    assert not (output / 'train' / 'datejust41').exists()

    mapping = json.loads((output / 'class_mapping.json').read_text(encoding='utf-8'))
    assert 'datejust' in mapping
    assert 'datejust41' not in mapping

def test_main_builds_dataset_from_raw_incoming(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    make_images(tmp_path / 'data' / 'raw_incoming', 'datejust', 10)
    make_images(tmp_path / 'data' / 'raw_incoming', 'submariner', 10)

    main()

    assert len(list_names(tmp_path / 'data' / 'processed' / 'train' / 'datejust')) == 7
    assert len(list_names(tmp_path / 'data' / 'processed' / 'train' / 'submariner')) == 7

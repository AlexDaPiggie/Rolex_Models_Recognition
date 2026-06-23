import json
import random
import shutil
from pathlib import Path
from src.collection.sources import VALID_LABELS

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
DEFAULT_TRAIN_RATIO = 0.7
DEFAULT_VAL_RATIO = 0.15
DEFAULT_TEST_RATIO = 0.15
LABEL_ALIASES = {
    'datejust41': 'datejust',
}

def image_files (class_dir: Path):
    return sorted (
        path 
        for path in class_dir.iterdir()
        if path.is_file() and path.suffix.lower() in 
        IMAGE_EXTENSIONS
    )

def discover_input_labels(input_root: Path):
    labels = sorted(
        path.name
        for path in input_root.iterdir()
        if path.is_dir() and image_files(path)
    )
    unknown_labels = [label for label in labels 
                      if label not in VALID_LABELS]
    if unknown_labels:
        raise ValueError(f"Unknown input label folders: {unknown_labels}")
    return labels

def final_label_for(raw_label: str):
    return LABEL_ALIASES.get(raw_label, raw_label)

def split_counts(
    total: int,
    train_ratio: float,
    val_ratio: float,
):
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    test_count = total - train_count - val_count
    return train_count, val_count, test_count

def clean_output_root (output_root: Path):
    if output_root.exists():
        shutil.rmtree (output_root)
    for split in ('train', 'val', 'test'): 
        (output_root / split).mkdir (
            parents=True,
            exist_ok=True
        )

def copy_split (files: list[Path], output_dir: Path): 
    output_dir.mkdir (parents = True, exist_ok=True)
    for source_path in files: 
        shutil.copy2(source_path, output_dir / source_path.name)


def write_class_mapping (output_root: Path, labels: list[str]):
    mapping = {label: index for index, label in enumerate(labels)}
    
    # write json files with good formats
    (output_root / 'class_mapping.json').write_text (
        json.dumps(mapping, indent = 2, sort_keys = True) + '\n',
        encoding = 'utf-8',
    )

def build_dataset (
    input_root: Path,
    output_root: Path,
    seed: int = 42,
    train_ratio: float = DEFAULT_TRAIN_RATIO,
    val_ratio: float = DEFAULT_VAL_RATIO,
    test_ratio: float = DEFAULT_TEST_RATIO,
):
    raw_labels = discover_input_labels(input_root)
    files_by_label = {}
    for raw_label in raw_labels:
        final_label = final_label_for(raw_label)
        files_by_label.setdefault(final_label, []).extend(
            image_files(input_root / raw_label)
        )
    labels = sorted(files_by_label)
    
    clean_output_root(output_root)
    randomizer = random.Random(seed)

    for label in labels:
        files = sorted(files_by_label[label])
        train_count, val_count, _ = split_counts(
            len(files),
            train_ratio,
            val_ratio,
        )
        shuffled_files = files[:]
        randomizer.shuffle (shuffled_files)
        train_files = shuffled_files[:train_count]
        val_files = shuffled_files[train_count : train_count + val_count]
        test_files = shuffled_files[train_count + val_count :]
        
        copy_split (train_files, output_root / 'train' / label)
        copy_split (val_files, output_root / 'val' / label)
        copy_split (test_files, output_root / 'test' / label)

    write_class_mapping(output_root, labels)

def main(): 
    build_dataset(
        input_root=Path('data/raw_incoming'),
        output_root=Path('data/processed'),
        seed = 42,
        train_ratio = DEFAULT_TRAIN_RATIO,
        val_ratio = DEFAULT_VAL_RATIO,
        test_ratio= DEFAULT_TEST_RATIO,
    )

if __name__ == "__main__": 
    main()

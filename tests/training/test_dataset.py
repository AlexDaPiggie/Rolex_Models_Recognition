import json
from PIL import Image
import torch 

from src.training.dataset import (
    IMAGE_SIZE,
    build_transforms,
    load_class_mapping,
    load_class_names,
)

def test_load_class_mapping_json (tmp_path):
    processed = tmp_path / 'processed'
    processed.mkdir()
    (processed / 'class_mapping.json').write_text (
        json.dumps ({'datejust': 0, 'gmt_master': 1, 'submariner': 2}),
        encoding = 'utf-8',
    )
    mapping = load_class_mapping (processed)
    assert mapping == {'datejust': 0, 'gmt_master': 1, 'submariner': 2}

def test_load_class_names_return_index(tmp_path): 
    processed = tmp_path / 'processed'
    processed.mkdir()
    (processed / 'class_mapping.json').write_text (
        json.dumps ({'submariner': 2, 'datejust': 0, 'gmt_master': 1}),
        encoding = 'utf-8',
    )
    class_names = load_class_names(processed)
    assert class_names == ['datejust', 'gmt_master', 'submariner']

def test_build_transforms():
    image = Image.new ('RGB', (80, 60), color = 'white')
    tensor = build_transforms(train = False)(image)
    assert isinstance(tensor, torch.Tensor)
    assert tuple (tensor.shape) == (3, IMAGE_SIZE, IMAGE_SIZE)
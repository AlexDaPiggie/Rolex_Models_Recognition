import torch 
import torch.nn as nn
from pathlib import Path
from src.training.train import save_checkpoint

def test_save_checkpoint(tmp_path): 
    model = nn.Linear (2, 3)
    output = tmp_path / 'rolex_model_classifier.pt'
    save_checkpoint (
        output_path = output,
        model = model,
        class_names = ['datejust', 'submariner', 'gmt_master'], 
        image_size = 224,
    )

    checkpoint = torch.load (output, map_location = 'cpu')
    assert checkpoint['class_names'] == ['datejust', 'submariner', 'gmt_master']
    assert checkpoint['image_size'] == 224
    assert 'model_state_dict' in checkpoint

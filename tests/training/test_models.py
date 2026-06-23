import torch 
from src.training.models import create_model

def test_create_model ():
    model = create_model (num_classes = 4, pretrained=False)
    model.eval()
    with torch.no_grad():
        output = model (torch.zeros(2, 3, 224, 224))
    assert tuple (output.shape) == (2, 4)
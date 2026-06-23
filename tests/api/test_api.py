from io import BytesIO
from fastapi.testclient import TestClient
from PIL import Image
import torch 
import torch.nn as nn
from src.api import main

class FixedModel (nn.Module):
    def forward (self, images):
        return torch.tensor ([[0.0, 3.0, 1.0]])
    
def make_upload_image():
    image = Image.new('RGB', (64, 64), color = 'white')
    buffer = BytesIO()
    image.save (buffer, format = 'JPEG')
    buffer.seek (0)
    return buffer

def test_predict_return_probabilities (monkeypatch): 
    monkeypatch.setattr(main, 'model', FixedModel())
    monkeypatch.setattr(main, 'class_names', ['datejust', 'gmt_master', 'submariner'])
    client = TestClient(main.app)
    response = client.post (
        '/predict',
        files = {'file': ('watch.jpg', make_upload_image(), 'iamge/jpeg')},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['predicted_class'] == 'gmt_master'
    assert body['confidence'] > 0.8
    assert set(body['probabilities']) == {'datejust', 'gmt_master', 'submariner'}
    
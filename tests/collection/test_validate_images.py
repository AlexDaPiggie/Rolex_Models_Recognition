from pathlib import Path
from PIL import Image
from src.collection.validate_images import validate_image

def test_validate_image (tmp_path: Path): 
    image_path = tmp_path / 'watch.jpg'
    Image.new ('RGB', (500, 500), color = 'white').save (image_path)
    result = validate_image (image_path, min_size = 224)
    assert result.is_valid is True 
    assert result.width == 500
    assert result.height == 500
    assert result.sha256
    assert result.perceptual_hash
    

def test_validate_image_reject (tmp_path: Path): 
    image_path = tmp_path / 'watch.jpg'
    Image.new ('RGB', (50, 50), color = 'white').save (image_path) 
    result = validate_image (image_path, min_size = 224)
    assert result.is_valid is False
    assert result.rejection_reason == 'image_too_small'


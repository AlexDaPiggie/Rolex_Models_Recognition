from pathlib import Path
from unittest.mock import Mock, patch
from PIL import Image
from src.collection.sources import ImageCandidate
from src.collection.collect_images import collect_images
from src.collection.sources import SwissWatchExpoSource

def test_collect_images(tmp_path: Path): 
    source = Mock()
    source.collect.return_value = [
        ImageCandidate(
            label='submariner',
            source_name='alex',
            listing_title='Rolex Submariner',
            listing_url='https://example.com/listing',
            image_url='https://example.com/image.jpg',
        )
    ]

    image_path = tmp_path / 'source.jpg'
    Image.new('RGB', (500, 500), color = 'white').save (image_path)
    image_bytes = image_path.read_bytes()

    response = Mock() 
    response.content = image_bytes
    response.raise_for_status = Mock() 

    with patch ('src.collection.collect_images.get_source', return_value = source), patch ('src.collection.collect_images.requests.get', return_value = response): 
        count = collect_images ( 
            source_name = 'alex', 
            label = 'submariner', 
            limit = 1, 
            output_root = tmp_path / 'raw_incoming', 
            manifest_path = tmp_path / 'manifests' / 'images.csv', 
        )
    assert count == 1
    assert len (list ((tmp_path / 'raw_incoming' / 'submariner').glob ('*.jpg'))) == 1
    manifest_text = (tmp_path / 'manifests' / 'images.csv').read_text (encoding = 'utf-8')
    assert 'submariner' in manifest_text
    assert 'downloaded' in manifest_text


def test_swisswatchexpo(): 
    html = """
    <html>
        <body>
            <div class = 'product_box catalog'>
                <a href = '/rolex-submariner-16610-watch.html'>
                    <img src = '/images/rolex-submariner.jpg' alt = 'Rolex Submariner'>
                </a>
            </div>
        </body
    </html>
    """
    
    response = Mock()
    response.text = html
    response.raise_for_status = Mock()

    with patch ('src.collection.sources.requests.get', return_value = response) as mock_get:
        source = SwissWatchExpoSource()
        candidates = source.collect (label = 'submariner', limit = 1)

    mock_get.assert_called_once()
    assert len(candidates) == 1
    assert candidates[0].label == 'submariner'
    assert candidates[0].source_name == 'swisswatchexpo'
    assert 'submariner' in candidates[0].listing_title.lower()
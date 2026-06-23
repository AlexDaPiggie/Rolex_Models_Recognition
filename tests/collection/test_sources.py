from src.collection.sources import ImageCandidate, validate_label, parse_product_images
from unittest.mock import Mock, patch
from src.collection.sources import get_source

def test_image_candidate_source_information(): 
    candidate = ImageCandidate(
        label = 'submariner',
        source_name = 'example',
        listing_title = 'Rolex Submariner', 
        listing_url = 'https://example.com/listing', 
        image_url = 'https://example.com/image.jpg', 
    )
    assert candidate.label == 'submariner'
    assert candidate.source_name == 'example'
    assert candidate.listing_title == 'Rolex Submariner'
    assert candidate.listing_url == 'https://example.com/listing'
    
def test_validate_accept_known_labels (): 
    validate_label('datejust')
    validate_label('submariner')

def test_validate_reject_unknown_labels(): 
    try:
        validate_label('speedmaster')
    except ValueError as error:
        assert 'Label not known' in str (error)

def test_parse_extract_produce_images(): 
    html = """
    <html>
      <head><title>Rolex Submariner Watches</title></head>
      <body>
        <img class="site-logo" src="/logo.png" />
        <div class="product-card">
          <a href="/listing/submariner-1">
            <img src="/images/submariner-front.jpg" alt="Rolex Submariner black dial" />
          </a>
        </div>
        <div class="product-card">
          <a href="/listing/submariner-2">
            <img data-src="/images/submariner-side.jpg" alt="Rolex Submariner side profile" />
          </a>
        </div>
      </body>
    </html>
    """

    candidates = parse_product_images(
        html=html,
        page_url='https://example.com/rolex-submariner',
        label = 'submariner', 
        source_name = 'example',
        product_selector = '.product-card',
    )

    assert len(candidates) == 2
    assert candidates[0].image_url == 'https://example.com/images/submariner-front.jpg'
    assert candidates[0].listing_url == 'https://example.com/listing/submariner-1'
    assert candidates[1].image_url == 'https://example.com/images/submariner-side.jpg'

def test_parse_reject_invalid_label(): 
    try: 
        parse_product_images(
            html = '<html></html',
            page_url = 'https://example.com', 
            label = 'omega', 
            source_name = 'example', 
            product_selector = '.product-card', 
        )
    except ValueError as error: 
        assert "Label not known" in str(error)

    
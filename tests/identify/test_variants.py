import json
from pathlib import Path
from src.identify.variants import load_catalog, variants_family

def test_load_variant_catalog (tmp_path):
    catalog_path = tmp_path / 'rolex_variants.json'
    catalog_path.write_text (
        json.dumps (
            {
                'gmt_master': [
                    {
                        'id': 'gmt_pepsi',
                        'display_name': 'Rolex GMT Master II Pepsi',
                        'reference_numbers': ['126710BLRO'],
                        'clip_text': 'Rolex GMT-Master II'
                    }
                ],
                'submariner': [
                    {
                        'id': 'submariner_black_date',
                        'display_name': 'Rolex Submariner Date Black',
                        'reference_examples': ['126610LN'],
                        'clip_text': 'Rolex Submariner with black bezel',
                    }
                ],
            }
        ),
        encoding = 'utf-8',
    )

    catalog = load_catalog(catalog_path)

    assert catalog['gmt_master'][0]['display_name'] == 'Rolex GMT Master II Pepsi'
    assert catalog['submariner'][0]['display_name'] == 'Rolex Submariner Date Black'
    assert catalog['gmt_master'][0]['id'] == 'gmt_pepsi'
    assert catalog['submariner'][0]['clip_text'] == 'Rolex Submariner with black bezel'

def test_variants_family_empty(tmp_path):
    catalog_path = tmp_path / 'rolex_variants.json'
    catalog_path.write_text (json.dumps ({'submariner': []}), 
                             encoding = 'utf-8')
    
    catalog = load_catalog(catalog_path)
    assert variants_family(catalog, 'daytona') == []
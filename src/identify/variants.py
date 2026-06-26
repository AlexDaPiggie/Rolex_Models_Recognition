import json 
from pathlib import Path
Variant = dict[str, object]
VariantCatalog = dict[str, list[Variant]]

'''
This file is to help processing the catalogs of Rolex models
- This catalog helps the CLIP model to check for reconizable models
'''

def load_catalog (catalog_path: Path):
    return json.loads(catalog_path.read_text (encoding = 'utf-8'))

def variants_family(catalog: VariantCatalog, family: str): 
    return catalog.get (family, [])
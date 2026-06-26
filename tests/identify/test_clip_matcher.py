from PIL import Image
from src.identify.clip_matcher import rank_variants
class FakeDetector: 
    def __call__ (self, image, candidate_labels): 
        return [
            {
                "label": 'Rolex GMT-Master II with black and blue hour bezel',
                "score": 0.71,
            },

            {
                "label": 'Rolex GMT-Master II with red and blue hour bezel',
                "score": 0.22,
            }
        ]
    
def test_rank_variants_matched():
    image = Image.new ("RGB", (64, 64), color = "white")
    variants = [
        {
            "id": "gmt_batman", 
            "display_name": "Rolex GMT-Master II Batman",
            "reference_examples": ["126710BLNR"],
            "clip_text": "Rolex GMT-Master II with black and blue hour bezel",
        },

        {
            "id": "gmt_pepsi",
            "display_name": "Rolex GMT-Master II Pepsi",
            "reference_examples": ["126710BLRO"],
            "clip_text": "Rolex GMT-Master II with red and blue hour bezel"
        },
    ]

    results = rank_variants(image, variants,detector=FakeDetector(), top_k = 2)

    assert results["variant_status"] == "matched_known_variant"
    assert results["variant_candidates"][0]["id"] == "gmt_batman"
    assert results["variant_candidates"][0]["display_name"] == "Rolex GMT-Master II Batman"
    assert results["variant_candidates"][0]["score"] == 0.71
    assert results["variant_candidates"][0]["reference_examples"] == ["126710BLNR"]
    assert results["variant_candidates"][1]["id"] == "gmt_pepsi"

def test_rank_variants_empty():
    image = Image.new ('RGB', (64, 64), color = 'white')
    results = rank_variants(image, [], detector= FakeDetector())

    assert results == {
        "variant_status": "no_variants_available",
        "variant_note": "No variant catalog is available for this model",
        "variant_candidates": [],
    }

class LowConfidenceDetector:
    def __call__(self, image, candidate_labels):
        return [
            {
                "label": "Rolex GMT-Master II with black and blue hour bezel", 
                "score": 0.29},

            {
                "label": "Rolex GMT-Master II with red and blue hour bezel", 
                "score": 0.26},
        ]

def test_rank_variants_weak_matches():
    image = Image.new ('RGB', (64, 64), color = 'white')
    variants = [
        {
            'id': 'gmt_batmat',
            'display_name': 'Rolex GMT-Master II Batman',
            'reference_examples': ['126710BLNR'],
            'clip_text': 'Rolex GMT-Master II with black and blue hour bezel'
        },

        {
            'id': 'gmt_pepsi',
            'display_name': 'Rolex GMT-Master II Pepsi',
            'reference_examples': ['126710BLRO'],
            'clip_text': 'Rolex GMT-Master II with red and blue hour bezel',
        },
    ]

    results = rank_variants (
        image, 
        variants,
        detector = LowConfidenceDetector(),
        top_k = 2,
    )

    assert results['variant_status'] == 'closest_known_matches'
    assert results['variant_note'] == 'The exact variant may not be in the catalog; these are the closest known matches'
    assert len (results['variant_candidates']) == 2
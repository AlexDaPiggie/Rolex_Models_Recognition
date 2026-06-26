from PIL import Image
from transformers import pipeline

'''
This file implement the logic of the zero-shot clip model. This comes in action after the deeplearning model has predicted the Rolex model. It checks the model variants in the file rolex_variants.json to tell which specific variant that model is.
'''

MODEL_NAME = 'openai/clip-vit-large-patch14'
_detector = None

def get_detector(): 
    '''
    This function is to create and return the CLIP image classification pipeline. It loads the CLIP model only once the first time, and store it inside the global _detector to reuse in the future
    '''
    global _detector
    if _detector is None: 
        _detector = pipeline (
            task = 'zero-shot-image-classification',
            model = MODEL_NAME
        )
    return _detector

def rank_variants(
    image: Image.Image,
    variants: list[dict[str, object]],
    detector = None,
    top_k: int = 3,
):
    '''
    This function return the possible variant for the predicted Rolex model
    '''
    if not variants: 
        return {
            "variant_status": "no_variants_available",
            "variant_note": "No variant catalog is available for this model",
            "variant_candidates": [],
        }
    
    detector = detector or get_detector()
    labels = [str(variant["clip_text"]) for variant in variants]

    variants_by_label = {
        str (variant["clip_text"]): variant 
        for variant in variants
    }

    predictions = detector (image, candidate_labels = labels)
    ranked = []
    for prediction in predictions[:top_k]: 
        variant = variants_by_label[prediction["label"]]
        ranked.append (
            {
                "id": variant['id'],
                "display_name": variant["display_name"],
                "score": float (prediction ["score"]),
                "reference_examples": variant.get ("reference_examples", []),
            }
        )

    top_score = ranked[0]['score'] if ranked else 0.0
    second_score = ranked[1]['score'] if len (ranked) > 1 else 0.0 
    if top_score < 0.35 or top_score - second_score < 0.08:
        return {
            "variant_status": "closest_known_matches",
            "variant_note": "The exact variant may not be in the catalog; these are the closest known matches",
            "variant_candidates": ranked,
        }
    return {
        "variant_status": "matched_known_variant",
        "variant_note": "The top result is the strongest match among known catalog variants, not a guaranteed exact reference",
        "variant_candidates": ranked,
    }
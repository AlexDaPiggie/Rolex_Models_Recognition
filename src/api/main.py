from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
import torch
from src.training.dataset import build_transforms
from src.training.models import create_model
from src.identify.clip_matcher import rank_variants
from src.identify.variants import load_catalog, variants_family

VARIANT_CATALOG_PATH = Path ('src/identify/rolex_variants.json')
MODEL_PATH = Path ('models/rolex_classifier_model.pt')
app = FastAPI(title = 'Rolex Classifier')

variant_catalog = load_catalog(VARIANT_CATALOG_PATH)
device = torch.device ('cpu')
model = None
class_names = []

def load_model(): 
    global model, class_names
    if not MODEL_PATH.exists(): 
        return 
    checkpoint = torch.load (MODEL_PATH, map_location = device)
    class_names = checkpoint ['class_names']
    model = create_model (
        num_classes=len(class_names),
        pretrained=False,
    ).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

def decode_image (contents: bytes): 
    try: 
        return Image.open (BytesIO(contents)).convert ('RGB')
    except:
        raise HTTPException(status_code=400, detail = "There's something wrong with the uploaded image")

def get_model():
    global model
    if model is None: 
        load_model()
    return model

def predict_image (image: Image.Image): 
    if model is None or not class_names:
        get_model()

    transform = build_transforms(train = False)
    tensor = transform (image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim = 1)[0].cpu()

    predicted_index = int (probabilities.argmax().item())
    probabilities = {
        class_name: float (probabilities[index].item())
        for index, class_name in enumerate(class_names)
    }

    predicted_class = class_names[predicted_index]
    result =  {
        'predicted_class': predicted_class,
        'confidence': probabilities[class_names[predicted_index]],
        'probabilities': probabilities,
    }

    variants = variants_family(variant_catalog, predicted_class)
    result.update (rank_variants(image, variants))
    return result


@app.post ('/predict')
async def predict (file: UploadFile = File(...)): 
    contents = await file.read()
    image = decode_image (contents)
    return predict_image (image)


from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
import torch
from src.training.dataset import build_transforms
from src.training.models import create_model
from src.identify.clip_matcher import rank_variants
from src.identify.variants import load_catalog, variants_family
from src.identify.summary import format_summary

VARIANT_CATALOG_PATH = Path ('src/identify/rolex_variants.json')
MODEL_PATH = Path ('models/rolex_classifier_model.pt')
app = FastAPI(title = 'Rolex Classifier')

variant_catalog = load_catalog(VARIANT_CATALOG_PATH)
device = torch.device ('cpu')
model = None
class_names = []

def load_model(): 
    '''
    This functino is simply to load DL model to reuse it in the future
    '''
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
    '''
    This function is to convert input image in to bytes for model to process
    '''
    try: 
        return Image.open (BytesIO(contents)).convert ('RGB')
    except:
        raise HTTPException(status_code=400, detail = "There's something wrong with the uploaded image")

def get_model():
    '''
    This function is simply to fetch the DL model
    '''
    global model
    if model is None: 
        load_model()
    return model

def predict_image (image: Image.Image): 
    '''
    This function is to predict the Rolex model using Deep Learning model. And then, traverse through the variants description of that model to recognize the variant using zero-shot CLIP model. A summary of that data is also provided. 

    * result is first formatted with data output, including 3 tags: predicted_classs, confidence, and prob
    * result is then updaed with variant prediction using CLIP, (using rank_variants function)
    * result is eventually added with a summary of the output, providing concise semantic result instead of data
    '''
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
    probabilities = dict (
        sorted (
            probabilities.items(),
            key = lambda item: item[1],
            reverse = True,
        )
    )

    predicted_class = class_names[predicted_index]
    result =  {
        'predicted_class': predicted_class,
        'confidence': probabilities[class_names[predicted_index]],
        'probabilities': probabilities,
    }

    variants = variants_family(variant_catalog, predicted_class)
    result.update (rank_variants(image, variants))
    result['model_name'],  result['Prediction Summary'] = format_summary(result)
    return result


'''
FastAPI format to operate the project pipeline
'''
@app.post ('/predict')
async def predict (file: UploadFile = File(...)): 
    contents = await file.read()
    image = decode_image (contents)
    return predict_image (image)


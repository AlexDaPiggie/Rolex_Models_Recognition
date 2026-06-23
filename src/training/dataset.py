import json
from pathlib import Path
from torchvision import datasets, transforms

IMAGE_SIZE = 224 #resive for cnn models
IMAGENET_MEAN = (0.485, 0.456, 0.406) #normalizaation
IMAGENET_STD = (0.229, 0.224, 0.225) #standard deviation

def load_class_mapping (data_root: Path): 
    '''
    read the mapping from processded dataset and turn that to dictionary
    '''
    mapping_path = data_root / 'class_mapping.json'
    mapping = json.loads(mapping_path.read_text(encoding = 'utf-8'))
    return {str(label): int (index) for label, index in mapping.items()}

def load_class_names(data_root: Path):
    '''
    - Turn the .json files into a list of class names with correct numeric order
    - This is to verify the labels used in other steps
    '''
    mapping = load_class_mapping(data_root)
    return [label for label, _index in sorted (
        mapping.items(),
        key = lambda item: item[1]
    )]

def build_transforms (train: bool):
    '''
    Build dataset engine:
    - only do data augmentation if it's train
    '''
    if train:
        return transforms.Compose(
            [
                transforms.RandomResizedCrop(
                    IMAGE_SIZE,
                    scale = (0.75, 1.2),
                    ratio = (0.85, 1.3),
                ),
                transforms.RandomRotation(degrees=50),

                transforms.RandomPerspective(
                    distortion_scale=0.25,
                    p = 0.35,
                ),
                transforms.ColorJitter(
                    brightness=0.25,
                    contrast = 0.25,
                    saturation = 0.15,
                    hue = 0.03,
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    IMAGENET_MEAN,
                    IMAGENET_STD,
                ),
                transforms.RandomErasing(
                    p = 0.2,
                    scale = (0.02, 0.12),
                    ratio = (0.3, 3.3),
                ),
            ]
        )
    
    return transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )

def make_image_folder (data_root: Path, split: str, train: bool):
    '''
    This is to create a Pytorch dataset for one split
    '''
    split_root = data_root / split
    dataset = datasets.ImageFolder(
        split_root,
        transform = build_transforms(train = train),
    )
    expected_classes = load_class_names(data_root)
    if dataset.classes != expected_classes:
        raise ValueError(
            f"Class order in Image Folder: {dataset.classes} doesn't match classes order in class_mapping.json: {expected_classes}"
        )
    return dataset
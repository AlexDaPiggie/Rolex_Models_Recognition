import argparse 
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from src.training.dataset import make_image_folder
from src.training.models import create_model

def load_checkpoint (checkpoint_path: Path, device: torch.device):
    return torch.load (checkpoint_path, map_location = device)

def top_prediction (logits: torch.tensor, class_names: list[str]): 
    probabilities = torch.softmax (logits, dim = 1)[0]
    predicted_index = int (probabilities.argmax().item())
    probabilities = {
        class_name: float(probabilities[index].item())
        for index, class_name in enumerate(class_names)
    }
    return {
        'predicted_class': class_names[predicted_index],
        'confidence': probabilities[class_names[predicted_index]],
        'probabilities': probabilities,
    }

def evaluate_checkpoint(
    data_root: Path,
    checkpoint_path: Path,
    batch_size: int,
    num_workers: int,
):
    device = torch.device ('cpu')
    checkpoint = load_checkpoint(checkpoint_path, device)
    test_dataset = make_image_folder(data_root, 'test', train = False)
    class_names = checkpoint['class_names']

    test_loader = DataLoader(
        test_dataset,
        batch_size = batch_size,
        shuffle = False,
        num_workers = num_workers,
    )

    model = create_model(num_classes = len(class_names), pretrained=False).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    criterion = nn.CrossEntropyLoss()
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader: 
            images = images.to(device)
            labels = labels.to(device)
            logits = model (images)
            loss = criterion(logits, labels)
            total_loss += loss.item() * images.size (0)
            correct += (logits.argmax (dim = 1) == labels).sum().item()
            total += images.size (0)

    return total_loss / total, correct / total 

def parse_args():
    parser = argparse.ArgumentParser(description = 'Evaluate model')
    parser.add_argument('--batch-size', type = int, default = 8)
    return parser.parse_args()

def main(): 
    args = parse_args()
    test_loss, test_accuracy = evaluate_checkpoint(
        data_root = Path('data/processed'),
        checkpoint_path = Path('models/rolex_classifier_model.pt'),
        batch_size=args.batch_size,
        num_workers = 4,
    )
    print (f'test_loss = {test_loss:.4f} test_acc = {test_accuracy:.4f}')

if __name__ == "__main__":
    main()
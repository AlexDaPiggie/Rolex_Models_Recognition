import argparse
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from src.training.dataset import IMAGE_SIZE, load_class_names, make_image_folder
from src.training.models import create_model

def save_checkpoint (
    output_path: Path,
    model: nn.Module,
    class_names: list[str],
    image_size: int,
):
    output_path.parent.mkdir (parents = True, exist_ok=True)
    torch.save (
        {
            'model_state_dict': model.state_dict(),
            'class_names': class_names,
            'image_size': image_size,
            'model_name': 'efficientnet_b0',
        },
        output_path,
    )

def train_one_epoch (
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
): 
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        correct += (logits.argmax(dim = 1) == labels).sum().item()
        total += images.size(0)

    return total_loss / total, correct / total

def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)
            labels = labels.to(device)
            logits = model (images)
            loss = criterion (logits, labels)
            total_loss += loss.item() * images.size(0)
            correct += (logits.argmax (dim = 1) == labels).sum().item()
            total += images.size (0) 

        return total_loss / total, correct / total 
    
def parse_args():
    parser = argparse.ArgumentParser(description = 'train classifier model') 
    parser.add_argument('--epochs', type = int, default = 5)
    parser.add_argument('--batch-size', type = int, default = 8)
    parser.add_argument('--learning-rate', type = float, default = 1e-4)
    
    return parser.parse_args()

def main(): 
    args = parse_args()
    device = torch.device('cpu')
    data = Path ('data/processed')
    class_names = load_class_names(data)

    train_dataset = make_image_folder(data, 'train', train = True)
    val_dataset = make_image_folder(data, 'val', train = False)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle = True,
        num_workers = 4,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle = False,
        num_workers = 4
    )

    model = create_model (num_classes = len (class_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr = args.learning_rate)

    best_val_accuracy = -1.0
    for epoch in range (1, args.epochs + 1):
        train_loss, train_accuracy = train_one_epoch (
            model, train_loader, criterion, optimizer, device
        )
        val_loss, val_accuracy = evaluate_model (
            model, val_loader, criterion, device
        )
        print (
            f'epoch = {epoch}',
            f'train_loss = {train_loss:.4f} train_acc = {train_accuracy:.4f}',
            f'val_loss = {val_loss:.4f} val_acc = {val_accuracy:.4f}',
        )

        if val_accuracy > best_val_accuracy: 
            best_val_accuracy = val_accuracy
            save_checkpoint (
                Path('models/rolex_classifier_model.pt'),
                model,
                class_names, 
                IMAGE_SIZE,
            )

if __name__ == "__main__": 
    main()
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "model_state_dict.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMAGE_SIZE = 128
CLASS_NAMES = ["NORMAL", "PNEUMONIA"]


class SimpleCNN(nn.Module):
    """Chest X-ray pneumonia classifier used by the saved state_dict."""

    def __init__(self) -> None:
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32768, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv(x)
        return self.fc(x)


def load_pneumonia_model() -> SimpleCNN:
    """Load the pneumonia model into memory once."""
    model = SimpleCNN()
    state_dict = torch.load(MODEL_PATH, map_location=DEVICE)

    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()

    return model


model = load_pneumonia_model()


def preprocess_image(image_path: str | Path) -> torch.Tensor:
    """Apply the same input shape expected by SimpleCNN."""
    transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor(),
        ]
    )

    image = Image.open(image_path)
    image_tensor = transform(image).unsqueeze(0)

    return image_tensor.to(DEVICE)


def predict_pneumonia(image_path: str | Path) -> dict:
    """Predict NORMAL/PNEUMONIA from a chest X-ray image path."""
    image_tensor = preprocess_image(image_path)

    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.softmax(output, dim=1)[0]

    predicted_index = int(torch.argmax(probabilities).item())
    normal_probability = float(probabilities[0].item())
    pneumonia_probability = float(probabilities[1].item())

    return {
        "label": CLASS_NAMES[predicted_index],
        "confidence": float(probabilities[predicted_index].item()),
        "normal_probability": normal_probability,
        "pneumonia_probability": pneumonia_probability,
    }

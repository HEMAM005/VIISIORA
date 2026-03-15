import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms

app = FastAPI(title="VisionEstate AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

room_classes = ["Bathroom", "Bedroom", "Dining", "Kitchen", "Livingroom"]
furniture_classes = ["book", "chair", "laptop", "person", "table"]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])


class ImageRequest(BaseModel):
    image_path: str


def load_room_model():
    model = models.resnet50()
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, len(room_classes))
    model.load_state_dict(
        torch.load(os.path.join(BASE_DIR, "models", "room_classifier.pt"), map_location=device)
    )
    model.to(device)
    model.eval()
    return model


def load_furniture_model():
    model = models.resnet50()
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, len(furniture_classes))
    model.load_state_dict(
        torch.load(os.path.join(BASE_DIR, "models", "furniture_classifier.pt"), map_location=device)
    )
    model.to(device)
    model.eval()
    return model


room_model = load_room_model()
furniture_model = load_furniture_model()


def predict_label(model, image, labels):
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    return labels[predicted.item()], confidence.item()


def generate_tags(room, furniture):
    tags = [room]

    if furniture != "person":
        tags.append("Contains " + furniture.capitalize())

    if room == "Bedroom":
        tags.append("Comfortable Bedroom")
    elif room == "Livingroom":
        tags.append("Spacious Living Room")
    elif room == "Kitchen":
        tags.append("Modern Kitchen")
    elif room == "Bathroom":
        tags.append("Clean Bathroom")

    return tags


@app.get("/")
def home():
    return {"message": "VisionEstate AI Service Running"}


@app.post("/analyze")
def analyze(data: ImageRequest):
    image_path = data.image_path

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    image = Image.open(image_path).convert("RGB")
    room, room_confidence = predict_label(room_model, image, room_classes)
    furniture, furniture_confidence = predict_label(furniture_model, image, furniture_classes)

    return {
        "room_type": room,
        "room_confidence": round(room_confidence * 100, 2),
        "furniture_detected": furniture,
        "furniture_confidence": round(furniture_confidence * 100, 2),
        "tags": generate_tags(room, furniture)
    }

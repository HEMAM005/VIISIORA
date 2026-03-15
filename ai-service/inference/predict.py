import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Room Classes
room_classes = ["Bathroom", "Bedroom", "Dining", "Kitchen", "Livingroom"]

# Furniture Classes
furniture_classes = ["book", "chair", "laptop", "person", "table"]

# Image Transform
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485,0.456,0.406],
        [0.229,0.224,0.225]
    )
])

# Load Room Model
def load_room_model():

    model = models.resnet50()

    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, len(room_classes))

    model.load_state_dict(
        torch.load("../models/room_classifier.pt", map_location=device)
    )

    model.to(device)
    model.eval()

    return model


# Load Furniture Model
def load_furniture_model():

    model = models.resnet50()

    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, len(furniture_classes))

    model.load_state_dict(
        torch.load("../models/furniture_classifier.pt", map_location=device)
    )

    model.to(device)
    model.eval()

    return model


# Predict Room
def predict_room(model, image):

    img = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():

        outputs = model(img)

        probabilities = torch.softmax(outputs, dim=1)

        confidence, predicted = torch.max(probabilities, 1)

    return room_classes[predicted.item()], confidence.item()


# Predict Furniture
def predict_furniture(model, image):

    img = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():

        outputs = model(img)

        probabilities = torch.softmax(outputs, dim=1)

        confidence, predicted = torch.max(probabilities, 1)

    return furniture_classes[predicted.item()], confidence.item()


# Generate Smart Tags
def generate_tags(room, furniture):

    tags = []

    tags.append(room)

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


# Analyze Image
def analyze_image(image_path):

    if not os.path.exists(image_path):
        raise FileNotFoundError("Image not found")

    image = Image.open(image_path).convert("RGB")

    room_model = load_room_model()
    furniture_model = load_furniture_model()

    room, room_conf = predict_room(room_model, image)

    furniture, furn_conf = predict_furniture(furniture_model, image)

    tags = generate_tags(room, furniture)

    result = {

        "room_type": room,
        "room_confidence": round(room_conf * 100, 2),

        "furniture_detected": furniture,
        "furniture_confidence": round(furn_conf * 100, 2),

        "tags": tags
    }

    return result


# Test Run
if __name__ == "__main__":

    image_path = "C:\\Users\\ruthi\\Downloads\\visionestate-ai\\ai-service\\dataset\\rooms\\test\\Bedroom\\bed_3.jpg"

    result = analyze_image(image_path)

    print("\n===== AI ANALYSIS RESULT =====\n")

    print("Room Type:", result["room_type"])
    print("Confidence:", result["room_confidence"], "%")

    print("\nFurniture Detected:", result["furniture_detected"])
    print("Confidence:", result["furniture_confidence"], "%")

    print("\nGenerated Tags:")

    for tag in result["tags"]:
        print("-", tag)
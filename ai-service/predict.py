import numpy as np
import tensorflow as tf
from utils import preprocess_image

# Load model
model = tf.keras.models.load_model("model/room_classifier.h5")

class_names = [
    "bathroom",
    "bedroom",
    "dining",
    "gaming",
    "kitchen",
    "laundry",
    "living",
    "office",
    "terrace",
    "yard"
]

def predict_room(image_file):

    processed_image = preprocess_image(image_file)

    prediction = model.predict(processed_image)

    predicted_index = np.argmax(prediction)
    confidence = float(np.max(prediction))

    room_type = class_names[predicted_index]

    return room_type, confidence
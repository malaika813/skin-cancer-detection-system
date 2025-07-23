
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D,MaxPool2D, Flatten, Dense, Dropout, BatchNormalization



# Class index mapping
classes = {
    0: "Actinic Keratoses (Cancer)",
    1: "Basal Cell Carcinoma (Cancer)",
    2: "Benign Keratosis-like Lesions (Non-Cancerous)",
    3: "Dermatofibroma (Non-Cancerous)",
    4: "Melanocytic Nevi (Non-Cancerous)",
    5: "Vascular Lesions (Pre-cancerous)",
    6: "Melanoma (Cancer)",
    7: "Unknown / Non-cancer image"
}

# Define CNN model structure
def get_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(28, 28, 3)),
        MaxPool2D(), BatchNormalization(),

        Conv2D(64, (3, 3), activation='relu'),
        MaxPool2D(), BatchNormalization(),

        Conv2D(128, (3, 3), activation='relu'),
        MaxPool2D(), BatchNormalization(),

        Flatten(), Dropout(0.3),
        Dense(256, activation='relu'), BatchNormalization(), Dropout(0.3),
        Dense(128, activation='relu'), BatchNormalization(), Dropout(0.2),
        Dense(64, activation='relu'), BatchNormalization(),
        Dense(8, activation='softmax')
    ])

    model.load_weights("best_skin_model.h5")
    return model



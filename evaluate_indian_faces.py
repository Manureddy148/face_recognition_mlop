import json
import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def main():
    model = tf.keras.models.load_model("saved_models/pretrained_indian_faces.keras")
    with open("saved_models/pretrain_indian_faces_labels.json", encoding="utf-8") as f:
        names = json.load(f)

    # Path to the dataset
    dataset_path = os.path.join(
        os.path.expanduser("~"),
        ".cache",
        "kagglehub",
        "datasets",
        "anirudhsimhachalam",
        "indian-movie-faces-datasetimfdb-face-recognition",
        "versions",
        "1",
        "IMFDB FR dataset",
        "IMFDB FR dataset"
    )

    datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

    validation_generator = datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=16,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    y_pred = np.argmax(model.predict(validation_generator, verbose=1), axis=1)
    y_test = validation_generator.classes

    print("
Classification Report:")
    print(classification_report(y_test, y_pred, target_names=names))

    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        xticklabels=names,
        yticklabels=names,
        cmap="Blues",
    )
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig("saved_models/confusion_matrix_indian_faces.png")
    print("
Confusion matrix saved to saved_models/confusion_matrix_indian_faces.png")


if __name__ == "__main__":
    main()

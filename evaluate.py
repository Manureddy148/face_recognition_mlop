import json

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.datasets import fetch_lfw_people
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


def main():
    model = tf.keras.models.load_model("saved_models/pretrained_lfw.keras")
    with open("saved_models/pretrain_labels.json", encoding="utf-8") as f:
        names = json.load(f)

    lfw = fetch_lfw_people(min_faces_per_person=20, resize=1.0)
    images = tf.image.resize(
        np.stack([img[:, :, np.newaxis] for img in lfw.images], axis=0),
        (224, 224),
    )
    images = tf.image.grayscale_to_rgb(images).numpy() / 255.0
    labels = lfw.target

    _, x_test, _, y_test = train_test_split(
        images,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    y_pred = np.argmax(model.predict(x_test, verbose=1), axis=1)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=names))

    top_classes = np.argsort(np.bincount(y_test))[-10:]
    mask = np.isin(y_test, top_classes)
    cm = confusion_matrix(y_test[mask], y_pred[mask], labels=top_classes)

    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        xticklabels=[names[i] for i in top_classes],
        yticklabels=[names[i] for i in top_classes],
        cmap="Blues",
    )
    plt.title("Confusion Matrix - Top 10 Classes")
    plt.tight_layout()
    plt.savefig("saved_models/confusion_matrix.png")
    print("\nConfusion matrix saved to saved_models/confusion_matrix.png")


if __name__ == "__main__":
    main()

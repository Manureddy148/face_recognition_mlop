import json
import os

import numpy as np
import tensorflow as tf
from sklearn.datasets import fetch_lfw_people
from sklearn.model_selection import train_test_split
from tensorflow.keras import Model, layers, optimizers
from tensorflow.keras.applications import VGG16
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau


def main():
    print("Loading LFW dataset...")
    lfw = fetch_lfw_people(min_faces_per_person=20, resize=1.0)

    images = lfw.images
    labels = lfw.target
    names = lfw.target_names
    n_classes = len(names)

    print(f"Dataset: {len(images)} images, {n_classes} people")

    # Resize grayscale faces to 224x224 and convert to RGB for VGG16.
    images_resized = tf.image.resize(
        np.stack([img[:, :, np.newaxis] for img in images], axis=0),
        (224, 224),
    )
    images_rgb = tf.image.grayscale_to_rgb(images_resized).numpy()
    images_rgb = images_rgb / 255.0

    labels_onehot = tf.keras.utils.to_categorical(labels, n_classes)

    x_train, x_test, y_train, y_test = train_test_split(
        images_rgb,
        labels_onehot,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )
    print(f"Train: {len(x_train)}  Test: {len(x_test)}")

    base = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    base.trainable = False

    x = layers.GlobalAveragePooling2D()(base.output)
    x = layers.Dense(512)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(0.3)(x)
    output = layers.Dense(n_classes, activation="softmax")(x)

    model = Model(inputs=base.input, outputs=output)
    model.compile(
        optimizer=optimizers.Adam(1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    os.makedirs("saved_models", exist_ok=True)
    callbacks = [
        EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
        ModelCheckpoint("saved_models/pretrained_lfw.keras", save_best_only=True),
        ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-6),
    ]

    print("\nPhase 1: Training top layers (frozen base)...")
    model.fit(
        x_train,
        y_train,
        validation_data=(x_test, y_test),
        epochs=30,
        batch_size=16,
        callbacks=callbacks,
    )

    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    print("\nPretrain complete!")
    print(f"Test Accuracy : {acc * 100:.2f}%")
    print(f"Test Loss     : {loss:.4f}")

    with open("saved_models/pretrain_labels.json", "w", encoding="utf-8") as f:
        json.dump(list(names), f)

    print("Model saved to saved_models/pretrained_lfw.keras")


if __name__ == "__main__":
    main()

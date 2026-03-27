import json
import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras import Model, layers, optimizers
from tensorflow.keras.applications import VGG16
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def main():
    print("Loading Indian Movie Faces dataset...")
    
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

    # Using ImageDataGenerator to load images from directory
    datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True
    )

    train_generator = datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=16,
        class_mode='categorical',
        subset='training'
    )

    validation_generator = datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=16,
        class_mode='categorical',
        subset='validation'
    )
    
    n_classes = len(train_generator.class_indices)
    names = list(train_generator.class_indices.keys())
    print(f"Dataset: {train_generator.n} training images, {validation_generator.n} validation images, {n_classes} people")

    # Build the model
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
        ModelCheckpoint("saved_models/pretrained_indian_faces.keras", save_best_only=True),
        ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-6),
    ]

    print("\nPhase 1: Training top layers (frozen base)...")
    pretrain_epochs = int(os.getenv("PRETRAIN_EPOCHS", "30"))
    model.fit(
        train_generator,
        validation_data=validation_generator,
        epochs=pretrain_epochs,
        callbacks=callbacks,
    )

    loss, acc = model.evaluate(validation_generator, verbose=0)
    print("\nPretrain complete!")
    print(f"Validation Accuracy : {acc * 100:.2f}%")
    print(f"Validation Loss     : {loss:.4f}")

    with open("saved_models/pretrain_indian_faces_labels.json", "w", encoding="utf-8") as f:
        json.dump(names, f)

    print("Model saved to saved_models/pretrained_indian_faces.keras")


if __name__ == "__main__":
    main()

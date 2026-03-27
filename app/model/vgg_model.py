"""
VGG16 Transfer Learning model for face recognition.

Architecture:
  VGG16 (ImageNet weights, frozen base)
    → GlobalAveragePooling2D
    → Dense(512, ReLU) + BatchNorm + Dropout(0.5)
    → Dense(256, ReLU) + BatchNorm + Dropout(0.3)
    → Dense(num_classes, Softmax)

Supports incremental retraining when students are added/removed.
"""
import os
import json
import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras import layers, Model, optimizers
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
)

IMG_SIZE = (224, 224)
BATCH_SIZE = 16


def build_model(num_classes: int, fine_tune_from: int = None) -> Model:
    """
    Build a VGG16-based face classifier.

    Args:
        num_classes:     Number of student classes.
        fine_tune_from:  Layer index from which to unfreeze for fine-tuning.
                         None = keep entire base frozen (faster, fewer samples).
    """
    base = VGG16(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3),
    )
    base.trainable = False

    if fine_tune_from is not None:
        for layer in base.layers[fine_tune_from:]:
            layer.trainable = not isinstance(layer, tf.keras.layers.BatchNormalization)

    x = layers.GlobalAveragePooling2D()(base.output)

    x = layers.Dense(512)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(0.5)(x)

    x = layers.Dense(256)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(0.3)(x)

    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=base.input, outputs=outputs)
    return model


def compile_model(model: Model, learning_rate: float = 1e-4) -> Model:
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def get_data_augmentation():
    return tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.15),
        layers.RandomZoom(0.1),
        layers.RandomBrightness(0.2),
        layers.RandomContrast(0.2),
    ], name="augmentation")


def load_dataset(data_dir: str, class_labels: list[str], validation_split: float = 0.2):
    """
    Load face images from  data_dir/{reg_no}/*.jpg  structure.
    Returns (train_ds, val_ds).
    """
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=class_labels,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=validation_split,
        subset="training",
        seed=42,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=class_labels,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=validation_split,
        subset="validation",
        seed=42,
    )

    augment = get_data_augmentation()
    autotune = tf.data.AUTOTUNE

    # Normalise to [0,1] and augment training set
    train_ds = (
        train_ds
        .map(lambda x, y: (augment(x, training=True) / 255.0, y), num_parallel_calls=autotune)
        .prefetch(autotune)
    )
    val_ds = (
        val_ds
        .map(lambda x, y: (x / 255.0, y), num_parallel_calls=autotune)
        .prefetch(autotune)
    )
    return train_ds, val_ds


def train(
    data_dir: str,
    class_labels: list[str],
    save_dir: str,
    version: str,
    epochs: int = 30,
    fine_tune: bool = False,
) -> dict:
    """
    Full training pipeline. Returns metrics dict.
    """
    os.makedirs(save_dir, exist_ok=True)
    num_classes = len(class_labels)

    model_path = os.path.join(save_dir, f"model_v{version}.keras")
    labels_path = os.path.join(save_dir, f"labels_v{version}.json")

    train_ds, val_ds = load_dataset(data_dir, class_labels)

    # Phase 1: frozen base
    model = build_model(num_classes)
    model = compile_model(model, learning_rate=1e-3)

    callbacks = [
        EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
        ModelCheckpoint(model_path, save_best_only=True, monitor="val_accuracy"),
        ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-6),
    ]

    print(f"[TRAIN] Phase 1 – Frozen base, {num_classes} classes, {epochs} epochs")
    model.fit(train_ds, validation_data=val_ds, epochs=epochs, callbacks=callbacks)

    # Phase 2 (optional fine-tune)
    if fine_tune and num_classes >= 5:
        print("[TRAIN] Phase 2 – Fine-tuning last 4 VGG blocks")
        model = build_model(num_classes, fine_tune_from=-8)
        model.load_weights(model_path)
        model = compile_model(model, learning_rate=1e-5)
        model.fit(train_ds, validation_data=val_ds, epochs=10, callbacks=callbacks)

    with open(labels_path, "w") as f:
        json.dump(class_labels, f)

    loss, acc = model.evaluate(val_ds, verbose=0)
    print(f"[TRAIN] Final val_accuracy={acc:.4f}  val_loss={loss:.4f}")

    return {
        "version": version,
        "accuracy": float(acc),
        "loss": float(loss),
        "num_classes": num_classes,
        "model_path": model_path,
        "labels_path": labels_path,
        "class_labels": class_labels,
    }


"""
Trains a real speech-emotion classifier on the RAVDESS dataset
(Ryerson Audio-Visual Database of Emotional Speech and Song).

RAVDESS is a legitimate, peer-reviewed, openly licensed (CC BY-NC-SA 4.0)
dataset of actors reading fixed sentences in 8 emotions. This is a real,
defensible dataset for a speech-emotion-recognition demo -- NOT a dataset
about creditworthiness, honesty, or "intent to pay" (no such dataset
exists, because that is not something voice signals reliably predict).

--------------------------------------------------------------------
HOW TO GET THE DATA (must be done on your own machine -- this sandbox
has no general internet access):
  1. Go to https://zenodo.org/record/1188976 (the official RAVDESS release)
  2. Download "Audio_Speech_Actors_01-24.zip"
  3. Unzip it into backend/app/ml/data/ravdess/  so you have paths like
     backend/app/ml/data/ravdess/Actor_01/03-01-01-01-01-01-01.wav
--------------------------------------------------------------------

Usage:
    python -m app.ml.train_emotion_model

Produces: app/ml/emotion_model.joblib
"""
import glob
import os

import joblib
import librosa
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

from app.ml.feature_extraction import extract_features

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "ravdess")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "emotion_model.joblib")

# RAVDESS filename code -> emotion label (see dataset documentation)
RAVDESS_EMOTION_MAP = {
    "01": "neutral", "02": "calm", "03": "happy", "04": "sad",
    "05": "angry", "06": "fearful", "07": "disgust", "08": "surprised",
}


def load_dataset():
    files = glob.glob(os.path.join(DATA_DIR, "**", "*.wav"), recursive=True)
    if not files:
        raise FileNotFoundError(
            f"No .wav files found under {DATA_DIR}. "
            "Download RAVDESS first -- see the docstring at the top of this file."
        )

    X, y = [], []
    for path in files:
        code = os.path.basename(path).split("-")[2]  # third field = emotion code
        label = RAVDESS_EMOTION_MAP.get(code)
        if label is None:
            continue
        try:
            audio, sr = librosa.load(path, sr=None)
            X.append(extract_features(audio, sr))
            y.append(label)
        except Exception as e:
            print(f"Skipping {path}: {e}")

    return np.array(X), np.array(y)


def main():
    print("Loading RAVDESS dataset and extracting acoustic features...")
    X, y = load_dataset()
    print(f"Loaded {len(X)} samples across classes: {sorted(set(y))}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    clf = RandomForestClassifier(n_estimators=300, max_depth=None, random_state=42, class_weight="balanced")
    clf.fit(X_train_scaled, y_train)

    preds = clf.predict(X_test_scaled)
    print(classification_report(y_test, preds))

    joblib.dump({"model": clf, "scaler": scaler, "classes": sorted(set(y)), "source": "ravdess"}, MODEL_PATH)
    print(f"Saved trained model to {MODEL_PATH}")


if __name__ == "__main__":
    main()

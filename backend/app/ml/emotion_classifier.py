"""
Loads the trained speech-emotion model (see train_emotion_model.py) if
present, and runs inference on uploaded audio.

IMPORTANT SCOPE NOTE (read before wiring this into any decision logic):
This module classifies which of 8 broad emotions (RAVDESS taxonomy:
neutral, calm, happy, sad, angry, fearful, disgust, surprised) a short
speech clip most resembles. That is the full extent of what it does.

It does NOT and CANNOT determine:
  - whether someone is telling the truth
  - whether someone intends to repay a loan
  - a person's overall psychological state or diagnosis

Any product surface that shows this output MUST label it as "detected
speech emotion (experimental)" and must not present it as a credit or
trust signal without independent validation and regulatory review.
"""
import os
from typing import Optional

import joblib
import numpy as np

from app.ml.feature_extraction import extract_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), "emotion_model.joblib")

_cached = None


def _load():
    global _cached
    if _cached is None:
        if os.path.exists(MODEL_PATH):
            _cached = joblib.load(MODEL_PATH)
        else:
            _cached = None
    return _cached


def model_status() -> dict:
    bundle = _load()
    if bundle is None:
        return {
            "trained": False,
            "source": None,
            "note": ("No trained model found. Run "
                     "`python -m app.ml.train_emotion_model` after downloading RAVDESS "
                     "(see that file's docstring). Until then, /emotion falls back to a "
                     "clearly-labeled heuristic and should not be treated as real classifier output."),
        }
    return {"trained": True, "source": bundle.get("source"), "classes": bundle.get("classes")}


def classify_emotion(audio: np.ndarray, sr: int) -> dict:
    features = extract_features(audio, sr)
    bundle = _load()

    if bundle is None:
        # Deterministic, clearly-labeled heuristic fallback so the app is runnable
        # without the dataset -- this is NOT a trained classifier and must not be
        # presented to end users as one.
        energy = float(np.mean(features[26]))  # rms_mean index
        pitch_std = float(features[30])         # pitch_std_hz index
        guess = "calm" if pitch_std < 15 else "neutral"
        return {
            "mode": "HEURISTIC_FALLBACK_UNTRAINED",
            "predicted_emotion": guess,
            "confidence": None,
            "warning": "No trained model loaded -- this is a placeholder heuristic, not a real classification.",
        }

    model = bundle["model"]
    scaler = bundle["scaler"]
    X = scaler.transform(features.reshape(1, -1))
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    classes = model.classes_
    confidence = float(np.max(proba))

    return {
        "mode": "TRAINED_MODEL",
        "source_dataset": bundle.get("source"),
        "predicted_emotion": pred,
        "confidence": round(confidence, 3),
        "class_probabilities": {c: round(float(p), 3) for c, p in zip(classes, proba)},
    }

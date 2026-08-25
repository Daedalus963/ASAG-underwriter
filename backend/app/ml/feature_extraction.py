"""
Extracts a standard acoustic feature vector from a speech clip.
These are well-established features used in speech-emotion-recognition
research (MFCCs, pitch statistics, energy, zero-crossing rate) -- this
part is real, standard signal processing. What it feeds into afterwards
(a coarse emotion label) is a legitimate ML task; treating that label as
a proxy for "honesty" or "intent to repay a loan" is NOT scientifically
supported and this codebase does not claim otherwise (see ml/emotion_classifier.py).
"""
import numpy as np
import librosa


def extract_features(y: np.ndarray, sr: int) -> np.ndarray:
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    zcr = librosa.feature.zero_crossing_rate(y)
    zcr_mean = np.mean(zcr)

    rms = librosa.feature.rms(y=y)
    rms_mean = np.mean(rms)
    rms_std = np.std(rms)

    try:
        f0, voiced_flag, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )
        f0_voiced = f0[voiced_flag] if f0 is not None else np.array([])
        pitch_mean = float(np.nanmean(f0_voiced)) if f0_voiced.size else 0.0
        pitch_std = float(np.nanstd(f0_voiced)) if f0_voiced.size else 0.0
    except Exception:
        pitch_mean, pitch_std = 0.0, 0.0

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_mean = float(np.mean(centroid))

    feature_vector = np.concatenate([
        mfcc_mean, mfcc_std,
        [zcr_mean, rms_mean, rms_std, pitch_mean, pitch_std, centroid_mean],
    ])
    return feature_vector.astype(np.float32)


FEATURE_NAMES = (
    [f"mfcc_mean_{i}" for i in range(13)] +
    [f"mfcc_std_{i}" for i in range(13)] +
    ["zcr_mean", "rms_mean", "rms_std", "pitch_mean_hz", "pitch_std_hz", "spectral_centroid_mean"]
)

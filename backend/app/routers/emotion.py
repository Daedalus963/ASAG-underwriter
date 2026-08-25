import io

import librosa
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app import models
from app.security.auth import get_current_user
from app.security.validator import validate_audio_upload, MAX_AUDIO_BYTES
from app.ml.emotion_classifier import classify_emotion, model_status

router = APIRouter(prefix="/emotion", tags=["emotion"])


@router.get("/status")
def status(current_user: models.User = Depends(get_current_user)):
    return model_status()


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    content = await file.read()

    try:
        validate_audio_upload(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        audio, sr = librosa.load(io.BytesIO(content), sr=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not decode audio file: {e}")

    if audio.size == 0:
        raise HTTPException(status_code=400, detail="Decoded audio is empty/silent.")

    result = classify_emotion(audio, sr)
    result["duration_seconds"] = round(float(librosa.get_duration(y=audio, sr=sr)), 2)
    return result

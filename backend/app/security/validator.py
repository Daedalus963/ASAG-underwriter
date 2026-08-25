"""
Input validation and file-safety checks. Kept deliberately dependency-light
and explicit so it's easy to audit.
"""
import os

MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac"}

# Magic bytes for common audio containers
_MAGIC_SIGNATURES = {
    b"RIFF": "wav",       # WAV starts with RIFF....WAVE
    b"ID3": "mp3",        # MP3 with ID3 tag
    b"\xff\xfb": "mp3",   # MP3 without ID3 tag (MPEG frame sync)
    b"fLaC": "flac",
}


def validate_audio_upload(filename: str, content: bytes) -> None:
    """Raises ValueError if the upload fails any safety check."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise ValueError(f"Unsupported file extension '{ext}'. Allowed: {ALLOWED_AUDIO_EXTENSIONS}")

    if len(content) == 0:
        raise ValueError("Uploaded file is empty.")

    if len(content) > MAX_AUDIO_BYTES:
        raise ValueError(f"File exceeds {MAX_AUDIO_BYTES // (1024*1024)}MB limit.")

    header = content[:8]
    if not any(header.startswith(sig) for sig in _MAGIC_SIGNATURES):
        raise ValueError("File header does not match a recognized audio format (magic byte check failed).")


def safe_join(base_dir: str, filename: str) -> str:
    """Prevents path traversal when writing uploaded files to disk."""
    filename = os.path.basename(filename)  # strips any ../ or absolute path components
    full_path = os.path.abspath(os.path.join(base_dir, filename))
    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Invalid file path.")
    return full_path

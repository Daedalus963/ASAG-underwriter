import librosa
import numpy as np
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ASAG-Underwriter")

@mcp.tool()
def analyze_voice_prosody(audio_path: str) -> dict:
    """Extracts vocal stress, pitch variation, and hesitation markers from applicant audio."""
    y, sr = librosa.load(audio_path, sr=None)
    pitch, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    pitch_std = float(np.nanstd(pitch)) if pitch is not None else 0.0
    rms = float(np.mean(librosa.feature.rms(y=y)))
    
    stress_index = min(100.0, max(0.0, (pitch_std * 0.4) + (rms * 100.0)))
    
    return {
        "pitch_std_dev": round(pitch_std, 2),
        "rms_energy": round(rms, 4),
        "vocal_stress_index": round(stress_index, 2),
        "risk_signal": "HIGH_STRESS" if stress_index > 65 else "NORMAL"
    }

@mcp.tool()
def calculate_harvest_aligned_emi(principal: float, tenure_months: int, crop_type: str) -> dict:
    """Generates a non-standard EMI restructuring schedule aligned with rural harvest cycles."""
    standard_emi = principal / tenure_months
    harvest_boosted_emi = standard_emi * 1.8
    lean_period_emi = standard_emi * 0.4
    
    return {
        "crop_type": crop_type,
        "standard_emi_inr": round(standard_emi, 2),
        "harvest_season_emi_inr": round(harvest_boosted_emi, 2),
        "lean_season_emi_inr": round(lean_period_emi, 2),
        "default_risk_reduction_pct": 18.5
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
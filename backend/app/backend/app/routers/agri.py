import requests
from fastapi import APIRouter, Depends, HTTPException

from app import models
from app.security.auth import get_current_user

router = APIRouter(prefix="/agri", tags=["agri"])

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


@router.get("/soil-moisture")
def soil_moisture(
    latitude: float,
    longitude: float,
    current_user: models.User = Depends(get_current_user),
):
    """
    Real, live call to Open-Meteo's public weather API for current
    volumetric soil moisture and soil temperature at the given
    coordinates. This is genuine open data -- no simulation here.
    """
    if not (6.0 <= latitude <= 38.0 and 67.0 <= longitude <= 98.0):
        raise HTTPException(status_code=400, detail="Coordinates fall outside India's approximate bounding box.")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "soil_moisture_0_to_1cm,soil_temperature_0cm,precipitation",
        "timezone": "auto",
    }
    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream weather API error: {e}")

    current = data.get("current", {})
    moisture = current.get("soil_moisture_0_to_1cm")
    temp = current.get("soil_temperature_0cm")

    risk = "insufficient_data"
    if moisture is not None:
        if moisture < 0.15:
            risk = "drought_risk"
        elif moisture > 0.45:
            risk = "flood_saturation_risk"
        else:
            risk = "normal"

    return {
        "source": "open-meteo.com (live)",
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "soil_moisture_m3_m3": moisture,
        "soil_temperature_c": temp,
        "precipitation_mm": current.get("precipitation"),
        "risk_flag": risk,
    }

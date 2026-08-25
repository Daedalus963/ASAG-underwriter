# ASAG Underwriter — Field Ledger

A modern rural credit decisioning prototype that combines authenticated applicant workflows, live agronomic data, experimental voice analysis, and a transparent underwriting simulation in a single interactive product experience.

## Overview

ASAG Underwriter helps a field agent or underwriter review a farmer applicant through a structured digital workflow:

- create and manage applicants
- validate location and farm context
- pull live land-condition data using Open-Meteo
- upload audio for experimental emotional analysis
- generate a transparent assessment brief with explainable scoring

The product is intentionally designed to balance usability, auditability, and honest disclosure. It demonstrates how multi-modal signals can be visualized and evaluated in a rural lending workflow without pretending the final score is a production underwriting model.

---

## Why this project matters

Rural lending decisions often lack rich real-time context. This app brings together several relevant data streams into one operational dashboard:

- geospatial context for the farm location
- weather and soil inputs for current field conditions
- applicant profile data for loan and crop context
- voice-based behavioral signal for exploratory analysis
- risk reasoning expressed in a transparent, explainable format

This is not a black-box credit engine. It is a decision-support prototype built to help human underwriters review signals and understand how each factor contributes to the final recommendation.

---

## Core features

### 1. Secure authentication and access control

- user registration and login
- JWT-based session handling
- bcrypt password hashing
- role-based access patterns for different user types

### 2. Applicant intake workflow

- applicant creation form
- latitude and longitude validation
- crop and farm-size details
- loan amount tracking
- applicant queue and selection workflow

### 3. Live land intelligence

- real-time soil moisture, temperature, and precipitation lookups
- Open-Meteo integration for geographic coordinates
- applicant-specific farm data refreshed in the interface
- live status messaging for observed data sources

### 4. Experimental audio signal analysis

- audio file upload from the browser
- validation and safety checks before processing
- acoustic feature analysis using the project ML pipeline
- emotion classification output with confidence and warning handling

### 5. Transparent underwriting simulation

- simulated assessment engine for prototype decisioning
- detailed explanation of risk drivers
- disclosed scoring logic and contribution factors
- assessment result with clear interpretation and disclaimer

### 6. Interactive dashboard UI

- modern card-based layout
- tabbed navigation
- applicant workspace and assessment area
- live map panel for field context
- styled status, summary, and data lines

---

## Product flow

The user experience is structured around a simple decisioning flow:

1. Sign in or register
2. Create a new applicant
3. Review land and crop context
4. Fetch live agronomic observations
5. Upload applicant audio and analyze it
6. Run a prototype underwriting assessment
7. Review the explanation and risk summary

---

## Technology stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT authentication
- SlowAPI rate limiting
- SQLite database for local development

### Frontend

- HTML
- CSS
- JavaScript
- Fetch-based API communication
- Embedded map context and dashboard UX

### ML / analytics

- Librosa-based acoustic feature extraction
- speech-emotion classification pipeline
- RAVDESS-compatible training flow
- explainable prototype scoring logic

---

## Project structure

```text
ASAG_Underwriter/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── README.md
│   │   ├── security/
│   │   │   ├── auth.py
│   │   │   ├── rate_limit.py
│   │   │   └── validator.py
│   │   ├── routers/
│   │   │   ├── agri.py
│   │   │   ├-> applicants.py
│   │   │   ├── auth.py
│   │   │   ├── credit.py
│   │   │   └── emotion.py
│   │   └── ml/
│   │       ├── __init__.py
│   │       ├── emotion_classifier.py
│   │       ├── feature_extraction.py
│   │       ├── train_emotion_model.py
│   │       └── data/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── server.py
├── README.md
└── LICENSE
```

---

## Local setup

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Create a local environment configuration if needed and set your app secret.

```bash
# example flow
copy .env.example .env
```

Then start the API server:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API docs will be available at:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

### 2. Frontend

Serve the static web app from the frontend folder:

```bash
cd frontend
python -m http.server 5500
```

Then open:

- http://localhost:5500

The frontend is configured to talk to the backend at `http://127.0.0.1:8000` by default.

### 3. Optional map integration

To enable the Google Maps satellite panel, add the key before the app script loads:

```html
<script>
  window.ASAG_GOOGLE_MAPS_API_KEY = "YOUR_BROWSER_RESTRICTED_KEY";
</script>
```

This is optional and should be restricted to approved frontend origins in Google Cloud.

---

## Security and validation notes

The app includes several practical safeguards:

- bcrypt-based password hashing
- JWT session tokens
- role-aware access patterns
- server-side coordinate validation
- rate limiting for repeated requests
- file safety validation for uploaded audio content
- allow-listed CORS configuration

---

## Honest model disclosure

This project is intentionally transparent about what is real and what is simulated:

| Component | Status |
|---|---|
| User authentication and access control | Real |
| Input validation and rate limiting | Real |
| Live soil/weather data via Open-Meteo | Real |
| Audio-based emotion analysis pipeline | Real, when trained data is available |
| Final credit score and decision | Simulated prototype logic |
| Emotion-to-repayment hypothesis | Experimental and not established as a production underwriting signal |

The final decision output is built for demonstration and reviewability, not as a production-grade underwriting model. Every assessment includes a clear explanation of how the result was derived.

---

## Demo usage

A typical review flow looks like this:

```text
Register/Login
   ↓
Create applicant
   ↓
Fetch field conditions
   ↓
Upload audio clip
   ↓
Run assessment
   ↓
Review explanation and decision brief
```

---

## Contribution and future direction

This project is a strong foundation for a broader rural credit intelligence platform. Potential next steps include:

- stronger model validation against repayment outcomes
- richer geospatial and weather features
- explainable policy tuning for underwriting teams
- expanded role-based workflows for regional officers and analysts
- production deployment patterns for cloud hosting and monitoring

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

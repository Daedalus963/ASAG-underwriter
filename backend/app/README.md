# ASAG-Underwriter — Field Ledger

A working prototype for the TVS Credit E.P.I.C 8.0 Analytics Challenge:
a rural-credit assistance tool that combines live satellite/weather soil
data with a speech-emotion classifier, wrapped in a real authenticated
web app.

## What's real vs. simulated (read this before presenting to a jury)

| Component | Status |
|---|---|
| Auth (JWT, bcrypt password hashing, RBAC) | **Real.** Production-grade pattern, tested. |
| Input validation, rate limiting, audio file safety checks | **Real.** |
| Soil moisture / temperature data (`/agri/soil-moisture`) | **Real live API call** to Open-Meteo. |
| Speech-emotion classifier (`/emotion/analyze`) | **Real ML**, once trained on RAVDESS (see below). Classifies into 8 broad emotions using standard acoustic features (MFCCs, pitch, energy). |
| Final credit "risk score" and decision (`/credit/assess`) | **Simulated.** A transparent, hand-written rule set built for this demo — not trained on real repayment outcomes. Every response includes a `disclaimer` field and a line-by-line `explanation` of how the number was produced. |
| "Emotion → intent to repay" link | **Not scientifically established.** The app labels this as an experimental signal everywhere it appears. Do not claim otherwise to the jury — the honest framing ("worth piloting and validating") is also the stronger one. |

## Project layout

```
asag_underwriter/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, rate-limit wiring
│   │   ├── config.py            # env-based settings
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   ├── models.py            # User, Applicant, Assessment tables
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── security/
│   │   │   ├── auth.py          # JWT + bcrypt + RBAC dependency
│   │   │   ├── rate_limit.py    # per-IP rate limiting
│   │   │   └── validator.py     # audio upload safety checks
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── applicants.py
│   │   │   ├── agri.py          # live Open-Meteo integration
│   │   │   ├── emotion.py       # audio upload + classification
│   │   │   └── credit.py        # simulated, fully-disclosed scoring
│   │   └── ml/
│   │       ├── feature_extraction.py   # librosa acoustic features
│   │       ├── train_emotion_model.py  # trains on real RAVDESS data
│   │       └── emotion_classifier.py   # loads model, runs inference
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── styles.css
    └── app.js
```

## Running it

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set a real SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(32))"

uvicorn app.main:app --reload --port 8000
```

API docs available at `http://127.0.0.1:8000/docs` once running.

### 2. Train the real emotion classifier (optional but recommended)

Without this step, `/emotion/analyze` still works but honestly reports
`HEURISTIC_FALLBACK_UNTRAINED` instead of a real classification.

1. Download `Audio_Speech_Actors_01-24.zip` from the official RAVDESS
   release: https://zenodo.org/record/1188976
2. Unzip into `backend/app/ml/data/ravdess/`
3. Run:
   ```bash
   cd backend
   python -m app.ml.train_emotion_model
   ```

### 3. Frontend

The frontend is plain HTML/CSS/JS — no build step needed.

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://127.0.0.1:5500`. It talks to the backend at
`http://127.0.0.1:8000` by default — override by setting
`window.ASAG_API_BASE` before `app.js` loads if you deploy the backend
elsewhere.

## Security notes for your write-up

- Passwords hashed with bcrypt (via passlib), never stored or logged in plaintext.
- JWT session tokens, 30-minute expiry by default.
- RBAC via `require_role()` dependency (available for admin-only endpoints — extend as needed).
- Coordinate inputs are bounds-checked server-side (India bounding box) via Pydantic `Field` constraints.
- Audio uploads are checked for extension, magic bytes, size cap (10MB), and path-traversal-safe filenames before processing.
- Per-IP rate limiting via `slowapi`.
- CORS is allow-listed, not wildcard, in `config.py`.

## For the jury / case-study writeup

Lead with the honest framing: this demonstrates *how* a multi-modal
rural credit signal pipeline could be built and audited, using two real
open data sources (satellite/weather telemetry, speech-emotion
research), stitched together with a transparent (not black-box) demo
scoring layer. The natural next step you'd propose to TVS Credit is a
supervised pilot validating whether the acoustic signal actually
correlates with repayment outcomes before any of it touches a real
underwriting decision.

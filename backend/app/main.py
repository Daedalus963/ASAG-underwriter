from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine
from app.security.rate_limit import limiter
from app.routers import auth, applicants, agri, emotion, credit

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description=(
        "Prototype rural-credit assistance platform for the TVS Credit E.P.I.C "
        "Analytics Challenge. See /credit assess responses for the disclaimer "
        "that applies to every simulated score."
    ),
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please slow down."})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(applicants.router)
app.include_router(agri.router)
app.include_router(emotion.router)
app.include_router(credit.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}

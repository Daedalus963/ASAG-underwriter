"""
Central configuration. All secrets are read from environment variables /
a local .env file -- NEVER hardcoded. Copy .env.example to .env and fill
in real values before running in anything beyond local dev.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Security ---
    # Generate a real one with: python -c "import secrets; print(secrets.token_hex(32))"
    secret_key: str = "CHANGE-ME-INSECURE-DEFAULT-DO-NOT-USE-IN-PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # --- Database ---
    database_url: str = "sqlite:///./asag.db"

    # --- Rate limiting ---
    rate_limit_per_minute: int = 30

    # --- CORS ---
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # --- App metadata ---
    app_name: str = "ASAG-Underwriter"
    environment: str = "development"


settings = Settings()

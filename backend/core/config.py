from typing import List, Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
import socket
import re
import logging

logger = logging.getLogger("vireoniq.config")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "VIREONIQ"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | staging | production

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Security
    SECRET_KEY: str = "vireoniq-production-secret-hmac-key-v6"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "RS256"
    PRIVATE_KEY_PATH: str = ".secrets/private_key.pem"
    PUBLIC_KEY_PATH: str = ".secrets/public_key.pem"

    # PostgreSQL
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "vireoniq"
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MongoDB (optional – used by some services for unstructured data)
    MONGO_URL: Optional[str] = None

    # Qdrant (vector store)
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: Optional[str] = None   # falls back to REDIS_URL at runtime
    CELERY_RESULT_BACKEND: Optional[str] = None  # falls back to REDIS_URL at runtime

    # AWS S3 (Resume Storage)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: Optional[str] = None
    S3_SIGNED_URL_EXPIRY: int = 3600
    # Alternate S3-compatible env-var names used by docker-compose
    S3_BUCKET: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    # LLM Settings
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    NVIDIA_NIM_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.3"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    NVIDIA_MODEL: str = "meta/llama-3.3-70b-instruct"
    DEFAULT_LLM_PROVIDER: str = "gemini"  # claude | openai | gemini | nvidia_nim | deepseek | ollama
    GEMINI_MODEL: str = "gemini-2.5-flash"
    INTERVIEW_MAX_TURNS: int = 10
    CLAUDE_MODEL: str = "claude-3-7-sonnet-20250219"

    # Judge0 (code execution sandbox)
    JUDGE0_API_URL: Optional[str] = None
    JUDGE0_API_KEY: Optional[str] = None

    # GitHub integration
    GITHUB_TOKEN: Optional[str] = None

    # OAuth – Google
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Communication services
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None

    # Public-facing URLs
    FRONTEND_URL: Optional[str] = None
    BACKEND_URL: Optional[str] = None

    # Razorpay (India-first Payments)
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = None

    # Observability
    SENTRY_DSN: Optional[str] = None
    ENABLE_ANALYTICS: bool = True

    # Email / SMTP
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM: str = "noreply@vireoniq.com"

    @property
    def async_database_url(self) -> str:
        # Check target database specification
        target_url = self.DATABASE_URL
        if target_url:
            if target_url.startswith("postgres://"):
                target_url = target_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif target_url.startswith("postgresql://"):
                target_url = target_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            # If SQLite is directly requested
            if "sqlite" in target_url:
                return target_url

            # Extract host and port from URL to verify TCP connectivity
            host = "localhost"
            port = 5432
            match = re.search(r"@([^:/]+)(?::(\d+))?", target_url)
            if match:
                host = match.group(1)
                if match.group(2):
                    port = int(match.group(2))

            postgres_available = False
            try:
                s = socket.create_connection((host, port), timeout=0.3)
                s.close()
                postgres_available = True
            except Exception:
                postgres_available = False

            if postgres_available:
                return target_url
            else:
                print(f"[Database Auto-Failover] PostgreSQL at {host}:{port} not reachable. Falling back to local SQLite (./placeiq.db).")
                return "sqlite+aiosqlite:///./placeiq.db"

        # Fallback to POSTGRES_SERVER / POSTGRES_PORT check
        postgres_available = False
        try:
            s = socket.create_connection((self.POSTGRES_SERVER, int(self.POSTGRES_PORT)), timeout=0.3)
            s.close()
            postgres_available = True
        except Exception:
            pass

        if postgres_available:
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            print(f"[Database Auto-Failover] PostgreSQL not reachable. Using local SQLite (./placeiq.db).")
            return "sqlite+aiosqlite:///./placeiq.db"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

settings = Settings()

from typing import List, Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AliasChoices, Field, field_validator
import os
import socket
import re
import structlog

logger = structlog.get_logger("vireoniq.config")
_INSECURE_DEFAULT_SECRET = "vireoniq-production-secret-hmac-key-v6"

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
    SECRET_KEY: str = _INSECURE_DEFAULT_SECRET
    CREDENTIAL_SIGNING_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "RS256"
    PRIVATE_KEY_PATH: str = Field(
        default=".secrets/private_key.pem",
        validation_alias=AliasChoices("PRIVATE_KEY_PATH", "JWT_PRIVATE_KEY_PATH"),
    )
    PUBLIC_KEY_PATH: str = Field(
        default=".secrets/public_key.pem",
        validation_alias=AliasChoices("PUBLIC_KEY_PATH", "JWT_PUBLIC_KEY_PATH"),
    )
    JWT_PRIVATE_KEY: Optional[str] = None
    JWT_PUBLIC_KEY: Optional[str] = None

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

    _resolved_dev_db_url: Optional[str] = None

    @staticmethod
    def _normalize_pg_url(url: str) -> str:
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @staticmethod
    def _probe_tcp_once(host: str, port: int) -> bool:
        try:
            with socket.create_connection((host, port), timeout=0.3):
                return True
        except OSError:
            return False

    @property
    def async_database_url(self) -> str:
        target_url = self.DATABASE_URL
        if target_url:
            target_url = self._normalize_pg_url(target_url)
            if "sqlite" in target_url:
                return target_url
            if self.is_production:
                return target_url
            if self._resolved_dev_db_url is not None:
                return self._resolved_dev_db_url

            host, port = "localhost", 5432
            match = re.search(r"@([^:/]+)(?::(\d+))?", target_url)
            if match:
                host = match.group(1)
                if match.group(2):
                    port = int(match.group(2))

            if self._probe_tcp_once(host, port):
                self._resolved_dev_db_url = target_url
            else:
                logger.warning(
                    "database_auto_failover",
                    host=host,
                    port=port,
                    fallback="sqlite+aiosqlite:///./vireoniq.db",
                )
                self._resolved_dev_db_url = "sqlite+aiosqlite:///./vireoniq.db"
            return self._resolved_dev_db_url

        if self.is_production:
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        if self._resolved_dev_db_url is not None:
            return self._resolved_dev_db_url

        if self._probe_tcp_once(self.POSTGRES_SERVER, int(self.POSTGRES_PORT)):
            self._resolved_dev_db_url = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            logger.warning(
                "database_auto_failover",
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                fallback="sqlite+aiosqlite:///./vireoniq.db",
            )
            self._resolved_dev_db_url = "sqlite+aiosqlite:///./vireoniq.db"
        return self._resolved_dev_db_url

    @property
    def is_production(self) -> bool:
        return (self.ENVIRONMENT or "").strip().lower() in {"production", "prod"}

    def validate_production_settings(self) -> None:
        """Reject insecure default secrets, DB passwords, SQLite failover, and wildcard CORS in production."""
        if not self.is_production:
            return

        errors: List[str] = []
        if not self.SECRET_KEY or self.SECRET_KEY == _INSECURE_DEFAULT_SECRET or len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be set to a strong non-default secret (>= 32 chars) in production.")
        if not self.CREDENTIAL_SIGNING_KEY or self.CREDENTIAL_SIGNING_KEY == _INSECURE_DEFAULT_SECRET or len(self.CREDENTIAL_SIGNING_KEY) < 32:
            errors.append("CREDENTIAL_SIGNING_KEY must be set to a dedicated non-default secret (>= 32 chars) in production.")

        if self.DATABASE_URL:
            lowered = self.DATABASE_URL.lower()
            if "sqlite" in lowered:
                errors.append("SQLite DATABASE_URL is forbidden in production.")
            if ":password@" in self.DATABASE_URL:
                errors.append("Default database password in DATABASE_URL is forbidden in production.")
        else:
            if not self.POSTGRES_PASSWORD or self.POSTGRES_PASSWORD == "password":
                errors.append("POSTGRES_PASSWORD must not use the default 'password' in production.")

        if "*" in [o.strip() for o in self.BACKEND_CORS_ORIGINS]:
            errors.append("Wildcard '*' in BACKEND_CORS_ORIGINS is forbidden when credentials are allowed.")

        if not (self.JWT_PRIVATE_KEY and self.JWT_PUBLIC_KEY):
            if not (os.path.exists(self.PRIVATE_KEY_PATH) and os.path.exists(self.PUBLIC_KEY_PATH)):
                errors.append(
                    f"JWT RSA key files not found ({self.PRIVATE_KEY_PATH}, {self.PUBLIC_KEY_PATH}) "
                    "and JWT_PRIVATE_KEY/JWT_PUBLIC_KEY env vars are unset."
                )

        if errors:
            raise RuntimeError("Invalid production configuration: " + " | ".join(errors))

settings = Settings()

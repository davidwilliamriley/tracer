"""
config.py — application configuration via environment variables.

All environment-dependent values live here. Nothing else in the codebase
should read os.environ directly — import `settings` from this module instead.

How it works:
  - pydantic-settings reads values from environment variables first,
    then falls back to a .env file if the variable is not set in the shell.
  - Field names match the .env variable names (case-insensitive).
  - SecretStr fields are redacted in logs and repr() output — their value
    is only accessible via .get_secret_value().

Usage:
    from config import settings

    db_url = settings.database_url
    secret  = settings.secret_key.get_secret_value()
    origins = settings.cors_origins

Adding a new setting:
  1. Add a field here with a type and default (or no default if required)
  2. Add it to .env.example with a placeholder value
  3. Set it in your real .env
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    database_url: str = "sqlite:///./db/graph.db"
    # For PostgreSQL: postgresql://user:password@host:5432/dbname

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    secret_key: SecretStr = SecretStr("change-me-before-deployment")
    # Generate a strong key with: python -c "import secrets; print(secrets.token_hex(32))"

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    # Comma-separated list of allowed origins.
    # Use "*" for development only — set explicit origins in production.
    cors_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse the comma-separated origins string into a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_name: str = "Tracer Graph API"
    app_version: str = "0.1.0"
    environment: str = "development"  # development | staging | production
    debug: bool = False

    # ------------------------------------------------------------------
    # Admin credentials (single-user mode)
    # ------------------------------------------------------------------
    # Plain password — development convenience only.
    # In production set ADMIN_PASSWORD_HASH to a bcrypt hash instead.
    admin_username: str = "admin"
    admin_password: str = "tracer-dev-password"
    admin_password_hash: str = ""   # overrides admin_password if set

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    # ------------------------------------------------------------------
    # pydantic-settings configuration
    # ------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",   # ignore unknown env vars rather than erroring
    )


# Single instance imported everywhere
settings = Settings()

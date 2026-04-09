"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the FastAPI application."""

    app_name: str = "Xindian_Cup"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_secret_key: str = "change-me"
    app_base_url: str = "http://127.0.0.1:8000"

    database_url: str = "postgresql+psycopg://xindian_cup:xindian_cup@127.0.0.1:5432/xindian_cup"
    session_expire_hours: int = 12
    email_verification_expire_minutes: int = 30

    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = "your-account@example.com"
    smtp_password: str = "change-me"
    smtp_from_email: str = "no-reply@example.com"

    line_channel_access_token: str = "change-me"
    line_channel_secret: str = "change-me"
    line_login_allowed_ids: str = ""
    line_login_cookie_name: str = "line_access"
    admin_api_token: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def parsed_line_login_allowed_ids(self) -> list[str]:
        """Return configured LINE user ids as a normalized list."""
        return [item.strip() for item in self.line_login_allowed_ids.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cache settings for the app lifecycle."""
    return Settings()

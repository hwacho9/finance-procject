from typing import List, Optional
import os


class Settings:
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Macro Finance Dashboard API"
    app_version: str = "1.0.0"
    debug: bool = True

    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000"]

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/macro_finance"

    # Redis
    redis_url: str = "redis://redis:6379"

    # External APIs
    alpha_vantage_api_key: Optional[str] = None
    fred_api_key: Optional[str] = None

    # Authentication
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Stripe
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # Data refresh settings
    market_data_cache_ttl: int = 60  # 1 minute
    economic_data_cache_ttl: int = 3600  # 1 hour

    def __init__(self):
        # Override with environment variables if they exist
        if os.getenv("DATABASE_URL"):
            self.database_url = os.getenv("DATABASE_URL")
        if os.getenv("REDIS_URL"):
            self.redis_url = os.getenv("REDIS_URL")
        if os.getenv("SECRET_KEY"):
            self.secret_key = os.getenv("SECRET_KEY")
        if os.getenv("DEBUG"):
            self.debug = os.getenv("DEBUG").lower() == "true"
        if os.getenv("CORS_ORIGINS"):
            self.cors_origins = [
                origin.strip() for origin in os.getenv("CORS_ORIGINS").split(",")
            ]
        if os.getenv("FRED_API_KEY"):
            self.fred_api_key = os.getenv("FRED_API_KEY")
        if os.getenv("ALPHA_VANTAGE_API_KEY"):
            self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")


# Global settings instance
settings = Settings()

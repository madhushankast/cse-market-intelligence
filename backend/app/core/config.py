from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "CSE Market Intelligence"
    ENVIRONMENT: str = "development"
    API_VERSION: str = "v1"
    DATABASE_URL: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

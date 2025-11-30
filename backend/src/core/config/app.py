from pydantic_settings import BaseSettings
from typing import Dict, Optional
from pydantic import Field

class AppConfig(BaseSettings):
    """Configurações da aplicação"""
    GEMINI_KEY: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Configurações OAuth - Google
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = Field(default="http://localhost:8000/auth/google/callback")

    # Configurações OAuth - Microsoft
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_REDIRECT_URI: Optional[str] = Field(default="http://localhost:8000/auth/microsoft/callback")

    # Configurações OAuth - GitHub
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = Field(default="http://localhost:8000/auth/github/callback")

    # Configurações OAuth - Apple
    APPLE_CLIENT_ID: Optional[str] = None
    APPLE_TEAM_ID: Optional[str] = None
    APPLE_KEY_ID: Optional[str] = None
    APPLE_PRIVATE_KEY: Optional[str] = None
    APPLE_REDIRECT_URI: Optional[str] = Field(default="http://localhost:8000/auth/apple/callback")

    class Config:
        env_file = ".env"
        case_sensitive = True

app_config = AppConfig()
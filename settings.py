import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # Discord OAuth
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_BOT_TOKEN: str
    DISCORD_REDIRECT_URI: str = "http://localhost:8000/auth/discord/callback"
    DISCORD_API_URL: str = "https://discord.com/api/v10"
    
    # Database
    DATABASE_URL: str = "sqlite:///./transmexico.db"
    BOT_DATABASE_PATH: str = "../bot/transmexico.db"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3001"
    
    # Discord Server Configuration
    DISCORD_SERVER_ID: int = 1057322159590088725
    DISCORD_STAFF_ROLE_ID: int = 1105015111942414356
    
    model_config = ConfigDict(
        env_file=str(env_path),
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sports Analytics System"
    # Fallback to sqlite if postgres is not available
    DATABASE_URL: str = "sqlite:///./sports_analytics.db"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

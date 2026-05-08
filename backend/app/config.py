from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Travel Planning Engine"
    API_V1_STR: str = "/api/v1"
    
    # GCP / Firebase
    GOOGLE_CLOUD_PROJECT: str = "your-gcp-project-id"
    FIREBASE_CREDENTIALS_PATH: str | None = None
    
    # Databases
    DATABASE_URL: str = "sqlite:///./sql_app.db" # Default to sqlite for local dev if not provided
    
    # AI / Maps
    VERTEX_AI_LOCATION: str = "us-central1"
    GOOGLE_MAPS_API_KEY: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()

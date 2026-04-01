from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application Metadata
    PROJECT_NAME: str = "SmartSpare AI"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api"
    ALGORITHM: str = "HS256"
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    GROQ_API_KEY: str

    # Pydantic V2 Configuration: Tell it to use the .env file and ignore extra variables
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def async_database_url(self) -> str:
        """Dynamically builds the async PostgreSQL connection string."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
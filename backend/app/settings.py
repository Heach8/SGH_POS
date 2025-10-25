from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Retail Sales App v3"
    DATABASE_URL: str = "sqlite:///./sales.db"
    JWT_SECRET: str = "change-me-in-prod"
    JWT_ALG: str = "HS256"
    XML_NAMESPACE: str = "urn:retail:sales:car"

settings = Settings()
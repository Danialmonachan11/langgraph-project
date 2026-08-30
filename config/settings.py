from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    checkpoint_db_url: str
    db_url: str
    openai_api_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

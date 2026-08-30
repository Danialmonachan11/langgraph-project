from functools import lru_cache
from sqlalchemy import Engine, create_engine
from config.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().db_url)

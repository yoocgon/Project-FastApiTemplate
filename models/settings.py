

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DATABASE_DIR: str
    DATABASE_NAME: str
    DATABASE_URL: str

    SQLITE_DIR: str
    SQLITE_NAME: str
    SQLITE_URL: str

    LOG_DIR: str
    DEBUG: bool
    #
    class Config:
        env_file = ".env"


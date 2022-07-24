
from pydantic import BaseSettings


class Settings(BaseSettings):
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: str = '6379'

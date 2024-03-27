from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    JWT_ACCESS_SECRET_KEY: SecretStr
    JWT_REFRESH_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
    )

    @property
    def database_url(self):
        return (
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )
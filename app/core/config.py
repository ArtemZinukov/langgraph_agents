from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    QA_THRESHOLD: float = 0.7
    MAX_REVISION_ITERATIONS: int = 2
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

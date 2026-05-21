from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "WANDERCHINA Community"
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    secret_key: str = "change-me"
    database_url: str = "postgresql+asyncpg://wander:wander@localhost:5432/wanderchina"
    database_url_sync: str = "postgresql://wander:wander@localhost:5432/wanderchina"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    elasticsearch_url: str = "http://localhost:9200"
    model_generation_url: str = "http://localhost:8001/generate"
    model_annotation_url: str = "http://localhost:8002/annotate"
    model_quality_url: str = "http://localhost:8003/evaluate"
    default_llm_provider: str = "deepseek"
    access_token_expire_minutes: int = 60
    upload_dir: str = "data/uploads"
    max_avatar_size_mb: int = 5
    allowed_avatar_types: str = "image/jpeg,image/png,image/webp,image/gif"


@lru_cache
def get_settings() -> Settings:
    return Settings()

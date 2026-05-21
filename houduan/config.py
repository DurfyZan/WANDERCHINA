from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 数据库配置
    db_user: str
    db_password: str
    db_host: str
    db_port: int = 3306
    db_name: str

    # JWT配置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 限流配置
    rate_limit: str = "5/minute"

    @property
    def database_url(self):
        return f"mysql+asyncmy://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

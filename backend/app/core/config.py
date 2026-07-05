from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase/Postgres connection string, e.g.:
    # postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
    database_url: str = "sqlite:///./smartfit_dev.db"

    log_level: str = "INFO"
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_prefix = "SMARTFIT_"


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    sqlite_db_path: str = "database.sqlite3"
    root_path: str = ""
    logging_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

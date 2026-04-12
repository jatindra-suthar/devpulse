import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings(BaseSettings):
    # GitHub
    github_token: str

    # watsonx
    watsonx_api_key: str
    watsonx_project_id: str
    watsonx_url: str
    watsonx_model_id: str

    # Database
    database_url: str

    # Email
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    email_from: str

    # App
    secret_key: str
    frontend_url: str

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

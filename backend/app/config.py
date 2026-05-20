from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Incident Management & RCA Automation Tool"
    database_url: str = "postgresql+psycopg2://incident:incident@db:5432/incidentdb"
    smtp_host: str = "localhost"
    smtp_port: int = 25
    smtp_sender: str = "alerts@example.com"
    alert_recipient: str = "devops@example.com"
    alert_throttle_seconds: int = 300
    monitoring_cron: str = "*/1 * * * *"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

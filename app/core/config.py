from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Azure Job Application Selector"
    app_env: str = "dev"

    azure_storage_connection_string: str = ""
    azure_storage_container_raw: str = "raw-documents"
    azure_document_intelligence_endpoint: str = ""
    azure_document_intelligence_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
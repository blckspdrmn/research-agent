import uuid

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None
    azure_openai_base_url: str
    azure_openai_api_key: str
    azure_openai_chat_deployment: str
    dummy_user_id: uuid.UUID  # TODO: のちほど認証を入れたら削除する
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

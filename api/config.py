import uuid

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None
    dummy_user_id: uuid.UUID  # TODO: のちほど認証を入れたら削除する
    model_config = {"env_file": ".env"}


settings = Settings()

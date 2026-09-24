from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None
    azure_openai_base_url: str
    azure_openai_api_key: str
    azure_openai_chat_deployment: str
    # Queue接続用。ローカルはAzurite、本番はStorage Accountの接続文字列
    azure_storage_connection_string: str
    # アクセストークンの検証に使う値。いずれもdiscoveryと、APIのアプリ登録から取る
    entra_issuer: str
    entra_jwks_url: str
    entra_api_client_id: str
    entra_required_scope: str
    # 本番全体で受け付けるリサーチの総回数（20260924以降）
    research_total_limit: int = 200
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

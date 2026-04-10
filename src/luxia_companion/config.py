from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    # OpenAI (embeddings + futuros agentes)
    openai_api_key: str
    openai_model_name: str = "gpt-4o"

    # Anthropic
    anthropic_api_key: str = ""

    # Knowledge Base
    chroma_persist_dir: str = "./chroma_data"
    knowledge_base_dir: str = "./knowledge_base"

    # Server
    port: int = 8000


settings = Settings()

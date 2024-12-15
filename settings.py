from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the Discord Birthday Bot.
    This class defines all required configuration parameters with their types
    and descriptions. It automatically loads values from environment variables
    and .env file.
    """

    discord_token: str = Field(description="Discord bot authentication token")
    channel_id: int = Field(description="Discord channel identifier")
    heartbeat_channel_id: int = Field(
        description="Channel identifier for heartbeat messages"
    )
    tenor_api_key: str = Field(description="Tenor API key for GIF fetching")
    claude_api_key: str = Field(
        description="Claude API key for generating birthday wishes"
    )
    claude_model: str = Field(
        description="Claude model to use for generating the birthday message"
    )
    tenor_query: str = Field(description="Query to search tenor API for relevant gifs")
    claude_prompt_path: str = Field(description="Path to prompt file (local or s3://)")
    data_path: str = Field(
        description="Path to CSV file containing user birthdays and information"
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", protected_namespaces=("settings_",)
    )


@lru_cache
def get_settings() -> Settings:
    """
    Create and return a cached Settings instance.
    """
    return Settings()  # type: ignore[call-arg]

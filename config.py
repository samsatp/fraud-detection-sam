from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model: str = 'baseline.pkl'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

config = Config()
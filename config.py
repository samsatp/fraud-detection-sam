from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Config(BaseSettings):
    model_path: str = os.path.join('models','model.pkl')
    scaler_path: str = os.path.join('models','scaler.pkl')
    features_path: str = os.path.join('models','features.json')
    db_url: str = 'sqlite:///output/sqlite.db'
    dst_table_name: str = 'fraud_predictions'
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Config()
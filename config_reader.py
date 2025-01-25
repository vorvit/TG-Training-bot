from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import os
import logging

LOG_LEVEL = logging.DEBUG

# Определяем путь к директории и файлу логов
log_directory = 'logs'
log_filename = 'bot_logs.log'
log_filepath = os.path.join(log_directory, log_filename)

# Проверяем существует ли директория и создаем ее, если нет
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Настраиваем логирование
logging.basicConfig(filename=log_filename, level=LOG_LEVEL,
                    format=' %(asctime)s - %(levelname)s - %(message)s')

class Settings(BaseSettings):

    bot_token: SecretStr
    weather_token: SecretStr
    nutritionix_app_id: SecretStr
    nutritionix_app_key: SecretStr

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()

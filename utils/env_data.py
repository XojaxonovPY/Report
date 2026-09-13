from os import getenv

from dotenv import load_dotenv

from utils.settings import Env_path

load_dotenv(Env_path)


class BotConfig:
    TOKEN = getenv('BOT_TOKEN')
    PAYMENT_CLICK_TOKEN = getenv('PAYMENT_CLICK_TOKEN')


class DBConfig:
    DB_URL = getenv('DB_URL')
    REDIS_URL = getenv('REDIS_URL')


class WebConfig:
    ADMIN_USERNAME = getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = getenv('ADMIN_PASSWORD')


class Config:
    bot = BotConfig()
    dp = DBConfig()
    web = WebConfig()

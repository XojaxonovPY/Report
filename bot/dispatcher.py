from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# from aiogram.fsm.storage.redis import RedisStorage
# from utils.env_data import Config as config

# storage = RedisStorage.from_url(config.dp.REDIS_URL)
# storage = MemoryStorage()
dp = Dispatcher()

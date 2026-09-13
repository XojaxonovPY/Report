import asyncio
import logging
import sys

import bcrypt
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.handlers import dp
from utils.env_data import BotConfig

# from aiogram.utils.i18n import I18n, FSMI18nMiddleware

TOKEN = BotConfig.TOKEN


async def set_bot_commands(bot: Bot):
    commands = [BotCommand(command="/start", description="Starting bot.")]
    await bot.set_my_commands(commands=commands)


async def main() -> None:
    # i18n = I18n(path='locales', default_locale='uz', domain='messages')
    # dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print(bcrypt.hashpw("3".encode(), salt=bcrypt.gensalt()).decode())
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

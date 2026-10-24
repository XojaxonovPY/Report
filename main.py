import asyncio
import logging
import sys

import bcrypt
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.handlers import dp
from db import engine
from db.models import metadata
from utils.env_data import BotConfig

# from aiogram.utils.i18n import I18n, FSMI18nMiddleware

TOKEN = BotConfig.TOKEN


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Starting bot.")
    ]
    await bot.set_my_commands(commands=commands)
    logging.info("Bot commands successfully have been set.")


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    logging.info("Database tables verified/created.")


async def on_startup(bot: Bot) -> None:
    await init_models()
    await set_bot_commands(bot)


async def on_shutdown() -> None:
    await engine.dispose()
    logging.info("Database connection closed.")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("The bot is starting up in polling mode...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logging.info("The bot session has closed.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        stream=sys.stdout,
    )
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("The bot has been stopped.")
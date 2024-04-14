from aiogram import Bot, Dispatcher
from handlers import handler
from aiogram.client.bot import DefaultBotProperties
from config.config import config
from loguru import logger

from middlewares import DbSessionMiddleware
from db import sessionmaker

import asyncio


async def main():
    logger.add(
        sink=config.logging.sink,
        format=config.logging.format,
        level=config.logging.level,
        rotation=config.logging.rotation,
        compression=config.logging.compression,
        serialize=config.logging.serialize,
    )

    bot: Bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=config.bot.parse_mode),
    )
    dp: Dispatcher = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    dp.include_router(handler.router)
    logger.info("Bot started successfuly!")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())

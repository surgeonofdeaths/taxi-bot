from aiogram import Bot, Dispatcher
from handlers import handler
from aiogram.client.bot import DefaultBotProperties
from config.config import settings
from db.database import sessionmaker
from keyboards.main_menu import set_main_menu

from loguru import logger

from middlewares import DbSessionMiddleware
import asyncio


async def main():
    logger.add(
        sink=settings.logging.sink,
        format=settings.logging.format,
        level=settings.logging.level,
        rotation=settings.logging.rotation,
        compression=settings.logging.compression,
        serialize=settings.logging.serialize,
    )

    bot: Bot = Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=settings.bot.parse_mode),
    )
    dp: Dispatcher = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    dp.include_router(handler.router)
    logger.info("Bot started successfuly!")

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())

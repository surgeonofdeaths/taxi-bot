import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from config.config import settings
from db.database import sessionmaker
from keyboards.main_menu import set_main_menu
from loguru import logger
from middlewares import DbSessionMiddleware
from misc import redis
from services.db_service import populate_lexicon


async def main():
    # TODO: restructure lines below
    async with sessionmaker() as session:
        await populate_lexicon(session)

    from handlers import admin, conversation, handler, order, user_misspell

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
    dp: Dispatcher = Dispatcher(storage=RedisStorage(redis))
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    dp.include_router(handler.router)
    dp.include_router(order.router)
    dp.include_router(conversation.router)
    dp.include_router(admin.router)
    dp.include_router(user_misspell.router)

    logger.info("Bot started successfuly!")

    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())

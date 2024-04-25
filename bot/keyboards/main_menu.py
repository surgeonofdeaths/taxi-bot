from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command="start",
            description="Отобразить меню",
        ),
        BotCommand(
            command="order",
            description="Заказать такси",
        ),
        BotCommand(
            command="help",
            description="О боте",
        ),
        BotCommand(
            command="contact",
            description="Связаться с оператором",
        ),
    ]
    await bot.set_my_commands(main_menu_commands)

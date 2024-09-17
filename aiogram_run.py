import asyncio
from create_bot import bot, dp
from handlers.start import start_router
from request_twitch_api.api_request import check_streamer_life
# from work_time.time_func import send_time_msg
from aiogram.types import BotCommand, BotCommandScopeDefault
from keyboards.keyboard_all import *


async def set_commands():
    commands = [BotCommand(command='start', description='Начало')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    await set_commands()
    asyncio.create_task(check_streamer_life())


async def main():
    dp.include_router(start_router)
    dp.startup.register(start_bot)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

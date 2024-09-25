import asyncio
from create_bot import bot, dp
from handlers.start import start_router
from request_twitch_api.api_request import check_streamer_life
# from work_time.time_func import send_time_msg
from aiogram.types import BotCommand, BotCommandScopeDefault
from keyboards.keyboard_all import *
from db_handler.db_class import UserDatabase


async def set_commands():
    commands = [BotCommand(command='start', description='Начало')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# def check_start_stream():-------------------------------------------------------------------------old method
#     db_user = UserDatabase(db_name="db_handler/tg_auth.db")
#     streamers = db_user.get_data_for_notif()
#     for i in streamers:
#         asyncio.create_task(check_streamer_life(i[0], i[1]))


def check_start_stream():
    # db = UserDatabase()
    # for i in db.get_id_tg_for_notif_distinct():
    asyncio.create_task(check_streamer_life(1022548979))


async def start_bot():
    await set_commands()
    check_start_stream()


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

import asyncio
import time
from datetime import datetime, timezone
import requests
import random
from aiogram.types import InlineKeyboardMarkup
from create_bot import bot
from keyboards.keyboard_all import keyboard_button_open_channel


async def check_streamer_life(id_tg, name):
    url = f'https://api.twitch.tv/helix/streams?user_login={name}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    status = False
    start_time = None
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            info_streamer = response_data['data']

            if info_streamer:
                if not status:
                    status = True
                    streamer_info = info_streamer[0]
                    streamer_name = streamer_info['user_name']
                    start_time = streamer_info['started_at']

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_open_channel(streamer_name)])
                    text = (f"🔴 <b>{streamer_name}</b> запустил трансляцию!\n"
                            f"\n"
                            f"<b>🎮 Категория текущей трансляции:</b> {streamer_info['game_name']}\n"
                            f"\n"
                            f"<b>📝 Описание текущей трансляции:</b> {streamer_info['title']}\n")
                    await bot.send_photo(
                        chat_id=id_tg,
                        photo=get_user_pf(streamer_name),
                        caption=text,
                        parse_mode='HTML',
                        reply_markup=keyboard)
            else:
                if status:
                    status = False
                    duration = time_difference_stream(start_time)
                    await bot.send_message(id_tg, f"⚫️ <b>{name}</b> завершил трансляцию.\n"
                                                  f"Трансляция длилась - {duration}", parse_mode='HTML')
                    start_time = None

        except requests.exceptions.RequestException as e:
            print(id_tg, f"Ошибка соединения с Twitch API: {e}")

        await asyncio.sleep(10)
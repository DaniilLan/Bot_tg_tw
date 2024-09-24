import asyncio
import time
from datetime import datetime, timezone
import requests
import random
from aiogram.types import InlineKeyboardMarkup
from create_bot import bot
from keyboards.keyboard_all import keyboard_button_open_channel


def get_user_id(name):
    url = f'https://api.twitch.tv/helix/users?login={name}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    response = requests.get(url, headers=headers).json()
    return response['data'][0]['id']


def get_random_follower(name):
    user_id = get_user_id(name)
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={user_id}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    user_names = []
    cursor = None
    while True:
        params = {'after': cursor} if cursor else {}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            followers_data = response.json()
            user_names.extend(follower['user_name'] for follower in followers_data.get('data', []))
            cursor = followers_data.get('pagination', {}).get('cursor')
            if not cursor:
                break
        else:
            return f"{response.status_code} - {response.text}"
    if user_names:
        return random.choice(user_names)
    else:
        return "Нет подписчиков."


def get_followed(name):
    url = f'https://tools.2807.eu/api/getfollows/{name}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            list_online = {}
            for streamer in data:
                if streamer['isLive']:
                    list_online[streamer['displayName']] = '🔴'
                else:
                    list_online[streamer['displayName']] = '⚫️'

            sorted_streamers = dict(sorted(list_online.items(), key=lambda item: item[1]))

            return sorted_streamers
        else:
            return False
    else:
        print(f"{response.status_code} - {response.text}")
        return False


def get_user_pf(name):
    url = f'https://api.twitch.tv/helix/users?login={name}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    response = requests.get(url, headers=headers).json()

    return response['data'][0]['profile_image_url']


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


def time_difference_stream(date_start_stream):
    date_1 = datetime.fromisoformat(date_start_stream.replace("Z", "+00:00"))
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    date_2 = datetime.fromisoformat(formatted_time.replace("Z", "+00:00"))
    time_difference = date_2 - date_1
    return time_difference


def get_info_stream(name):
    url = f'https://api.twitch.tv/helix/streams?user_login={name}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    response = requests.get(url, headers=headers)
    status = response.status_code
    response_data = response.json()
    return response_data, status


def get_streams(name1, name2, name3, name4):
    url = (f'https://api.twitch.tv/helix/streams/?'
           f'user_id={get_user_id(name1)}'
           f'&user_id={get_user_id(name2)}'
           f'&user_id={get_user_id(name3)}'
           f'&user_id={get_user_id(name4)}')
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    status = False
    start_time = None
    list_streams_life = []
    list_streams_of = ['a_hyena_dobr', 'eslcs', 'ubica', 'tabula_russia']
    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        now_streams = []
        if response_data and not status:
            for i in response_data['data']:
                if i['user_login'] not in list_streams_life:
                    list_streams_life.append(i['user_login'])
                    list_streams_of.remove(i['user_login'])
                    print(f"Стример {i['user_login']} онлайн")
                now_streams.append(i['user_login'])
            print("Cтримы онл", list_streams_life)
            print("Стримы офл", list_streams_of)
            diff_stream = list(set(list_streams_life) - set(now_streams))
            if diff_stream:
                if diff_stream not in list_streams_of:
                    list_streams_of.append(diff_stream[0])
                    list_streams_life.remove(diff_stream[0])
                    print(f"Стример {diff_stream[0]} завершил трансляцию!")
        time.sleep(5)


get_streams('a_hyena_dobr', 'eslcs', 'ubica', 'tabula_russia')

import asyncio
import time

import requests
import random
from create_bot import bot


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


async def check_streamer_life(name='iLame'):
    url = f'https://api.twitch.tv/helix/streams?user_login={name}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    status = False
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
                    text = (f"🔴 Стример <b>{streamer_info['user_name']}</b> запустил трансляцию!\n"
                            f"\n"
                            f"<b>🎮 Категория текущей трансляции:</b> {streamer_info['game_name']}\n"
                            f"\n"
                            f"<b>📝 Описание текущей трансляции:</b> {streamer_info['title']}")
                    await bot.send_message(1022548979, text=text, parse_mode='HTML')
            else:
                if status:
                    status = False
                    await bot.send_message(1022548979, f"⚫️ Стример <b>{name}</b> завершил трансляцию.", parse_mode='HTML')
        except requests.exceptions.RequestException as e:
            await bot.send_message(1022548979, f"Ошибка соединения с Twitch API: {e}")
        await asyncio.sleep(5)


def get_info_stream(name):
    url = f'https://api.twitch.tv/helix/streams?user_login={name}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    response = requests.get(url, headers=headers)
    response_data = response.json()
    return response_data

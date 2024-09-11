import requests
import random


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
        list_online = {}
        for streamer in data:
            if streamer['isLive']:
                list_online[streamer['displayName']] = '🔴'
            else:
                list_online[streamer['displayName']] = '⚫'

        sorted_streamers = dict(sorted(list_online.items(), key=lambda item: item[1]))

        return sorted_streamers
    else:
        print(f"{response.status_code} - {response.text}")
        return None


def get_user_pf(name):
    url = f'https://api.twitch.tv/helix/users?login={name}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    response = requests.get(url, headers=headers).json()

    return response['data'][0]['profile_image_url']


def get_info_channel(name):
    user_id = get_user_id(name)
    url = f'https://api.twitch.tv/helix/channels?broadcaster_id={user_id}'
    headers = {
        'Authorization': 'Bearer 2eawmkloujpadta8wjp0qaiyihggjb',
        'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'
    }
    response = requests.get(url, headers=headers)
    list_info = {}
    if response.status_code == 200:
        response = response.json()
        return response['data']
    else:
        print(f"{response.status_code} - {response.text}")
        return None


print(get_user_pf('tabula_russia'))
print(get_info_channel('tabula_russia'))
print(get_info_channel('ilame'))
print(get_info_channel('MILANRODD'))
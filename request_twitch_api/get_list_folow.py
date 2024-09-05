import requests


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

        # Сортируем имена стримеров по алфавиту
        sorted_streamers = dict(sorted(list_online.items(), key=lambda item: item[1]))

        return sorted_streamers  # Возвращаем отсортированный словарь
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")
        return None

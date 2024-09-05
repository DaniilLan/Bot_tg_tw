import requests
import json
from config import *


class ExchangeException(Exception):
    pass


class Exchange:
    @staticmethod
    def get_exchange(val1, val2, quantity):
        if val1.upper() == val2.upper():
            raise ExchangeException(f'Нельзя перевести одинаковые валюты {val2}.')
        try:
            quote_value1 = nac_ex[val1.upper()]
        except KeyError:
            raise ExchangeException(f'Не смог обработать валюту {val1}, проверьте список доступных валют.')

        try:
            quote_value2 = nac_ex[val2.upper()]
        except KeyError:
            raise ExchangeException(f'Не смог обработать валюту {val2}, проверьте список доступных валют.')
        try:
            quantity = float(quantity)
        except ValueError or SyntaxError or NameError:
            raise ExchangeException(f'Не смог обработать количество {quantity}.')
        if quantity <= 0:
            raise ExchangeException(f'Не смог обработать количество {quantity}, число должно быть больше 0')

        response = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={val1.upper()}&tsyms={val2.upper()}")
        response = response.content
        ex_info = json.loads(response)
        result = round(ex_info[val2.upper()] * float(quantity), 8)
        return result



from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


def keyboard_button_random_followers():
    keyboard = [InlineKeyboardButton(text=f"Розыгрыш среди фолловеров", callback_data=f"random_user")]
    return keyboard


def keyboard_button_check_streamers():
    keyboard = [InlineKeyboardButton(text=f"Просмотреть моих стримеров", callback_data=f"check_streamers")]
    return keyboard


def keyboard_button_list_streamers(status, name):
    keyboard = [InlineKeyboardButton(text=f"{status} {name}", callback_data=f"streamer_{name}")]
    return keyboard


def keyboards_button_bac_to_start():
    keyboards = [InlineKeyboardButton(text="В меню", callback_data="back_to_start")]
    return keyboards


def keyboards_button_bac_to_streamers():
    keyboards = [InlineKeyboardButton(text="Другие стримеры", callback_data="back_to_streamers")]
    return keyboards


def keyboard_button_re_write_nickname():
    keyboards = [InlineKeyboardButton(text="Написать другой ник-нейм", callback_data="write_nickname")]
    return keyboards


def keyboard_button_write_nickname():
    keyboards = [InlineKeyboardButton(text="Написать", callback_data="write_nickname")]
    return keyboards


def keyboard_button_re_roll_follow():
    keyboards = [InlineKeyboardButton(text="Перевыбрать", callback_data="re_roll_follow")]
    return keyboards


def keyboard_button_open_channel(name):
    keyboards = [InlineKeyboardButton(text="Канал на Twitch", callback_data="open_channel", url=f'https://www.twitch.tv/{name}')]
    return keyboards


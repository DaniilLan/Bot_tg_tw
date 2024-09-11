from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import InputMediaPhoto
from aiogram.utils.chat_action import ChatActionSender
from create_bot import bot
from keyboards.keyboard_all import *
from request_twitch_api.api_request import *
from requests.exceptions import ConnectionError
from db_handler.db_class import *
from functools import wraps
from wraps import *


start_router = Router()
user_nickname = {}
user_messages = {}
user_action = {}


@start_router.message(CommandStart())
@start_router.callback_query(F.data == "back_to_start")
@user_permission_required
async def cmd_start(event: Message | CallbackQuery):
    message = None
    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message
    elif isinstance(event, Message):
        message = event
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        keyboard_button_random_followers(),
        keyboard_button_check_streamers()
    ])
    text_command = ('Приветствую!\n'
                    'Ниже весь доступный функционал бота!')
    if isinstance(event, Message):
        await message.answer(text_command, reply_markup=keyboard)
    else:
        await message.edit_text(text_command, reply_markup=keyboard)


@start_router.callback_query(F.data == "write_nickname")
@user_permission_required
async def handle_wait_write_nickname(event: CallbackQuery):
    await event.answer()
    await event.message.edit_text("Жду твой ник-нейм на твиче ⏳")
    user_nickname[event.from_user.id] = True


@start_router.callback_query(F.data.startswith('streamer_'))
@user_permission_required
async def handle_streamer_click(event: CallbackQuery):
    await event.answer()
    streamer_name = event.data.replace('streamer_', '')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_open_channel(streamer_name),
                                                     keyboards_button_bac_to_streamers()])
    await event.message.delete()
    text = (f"Описание для стримера {streamer_name} в процессе. (пока ток фотку заливает)\n"
            f"")
    await bot.send_photo(
        chat_id=event.message.chat.id,
        photo=get_user_pf(streamer_name),
        reply_markup=keyboard,
        caption=text
    )


@start_router.callback_query(F.data == "back_to_streamers")
@user_permission_required
async def handle_back_to_streamers(event: CallbackQuery):
    user_id = event.from_user.id
    if user_id in user_nickname:
        nickname = user_nickname[user_id]
        followed_streamers = get_followed(nickname)
        if followed_streamers:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                                                keyboard_button_list_streamers(status, name)
                                                                for name, status in followed_streamers.items()
                                                            ] + [keyboards_button_bac_to_start()])

            if event.message.content_type == 'text':
                await event.message.edit_text("Вот твои стримеры:", reply_markup=keyboard)
            else:
                await event.message.delete()
                await event.message.answer("Вот твои стримеры:", reply_markup=keyboard)
        else:
            if event.message.content_type == 'text':
                await event.message.edit_text("Список стримеров пуст.")
            else:
                await event.message.delete()
                await event.message.answer("Список стримеров пуст.")
    else:
        keyboards = InlineKeyboardMarkup(inline_keyboard=[
            keyboard_button_write_nickname(),
            keyboards_button_bac_to_start()
        ])
        if event.message.content_type == 'text':
            await event.message.edit_text("Никнейм не найден, введите его снова.", reply_markup=keyboards)
        else:
            await event.message.delete()
            await event.message.answer("Никнейм не найден, введите его снова.", reply_markup=keyboards)


@start_router.callback_query(F.data == "check_streamers")
@user_permission_required
async def handle_write_nickname(event: CallbackQuery):
    await event.answer()
    user_action[event.from_user.id] = 'check_streamers'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        keyboard_button_write_nickname(),
        keyboards_button_bac_to_start()
    ])
    sent_message = await event.message.edit_text('Напиши свой ник-нейм на твиче, чтобы увидеть своих стримеров!',
                                                 reply_markup=keyboard)
    user_messages[event.message.from_user.id] = sent_message.message_id


@start_router.callback_query(F.data == "random_user")
@user_permission_required
async def handle_random_followers(event: CallbackQuery):
    await event.answer()
    user_action[event.from_user.id] = 'random_user'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        keyboard_button_write_nickname(),
        keyboards_button_bac_to_start()
    ])
    sent_message = await event.message.edit_text('Напиши свой ник-нейм на твиче, чтобы бот выбрал '
                                                 'одного победителя из твоих подписчиков!',
                                                 reply_markup=keyboard)
    user_messages[event.message.from_user.id] = sent_message.message_id


@start_router.message()
@user_permission_required
async def handle_message(event: Message):
    user_id = event.from_user.id
    if user_id in user_nickname and user_nickname[user_id] is True:
        nickname = event.text
        user_nickname[user_id] = nickname
        action = user_action.get(user_id)
        if action == 'check_streamers':
            try:
                followed_streamers = get_followed(nickname)
            except ConnectionError:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[keyboards_button_bac_to_start()]])
                return await event.answer("На данный момент сервис поиска стримеров перегружен.\n"
                                          "Попробуй другие функции бота или подожди пока все оживет ;)",
                                          reply_markup=keyboard)
            if followed_streamers is not None:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                                                    keyboard_button_list_streamers(status, name)
                                                                    for name, status in followed_streamers.items()
                                                                ] + [keyboards_button_bac_to_start()])

                async with ChatActionSender(bot=bot, chat_id=user_id, action="typing"):
                    await event.answer("Вот твои стримеры:", reply_markup=keyboard)
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    keyboard_button_re_write_nickname(),
                    keyboards_button_bac_to_start()
                ])
                await event.answer("Ты не подписан на стримеров или ты накосячил с ник-неймом!",
                                   reply_markup=keyboard)
        elif action == 'random_user':
            try:
                followed_streamers = get_random_follower('myrzen_u')
            except ConnectionError:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[keyboards_button_bac_to_start()]])
                return await event.answer("На данный момент сервис перегружен.\n"
                                          "Попробуй другие функции бота или подожди пока все оживет ;)",
                                          reply_markup=keyboard)
            if followed_streamers is not None:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_re_roll_follow(),
                                                                 keyboards_button_bac_to_start()])
                async with ChatActionSender(bot=bot, chat_id=user_id, action="typing"):
                    await event.answer(f"Вот твой победитель: {followed_streamers}", reply_markup=keyboard)
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    keyboard_button_re_write_nickname(),
                    keyboards_button_bac_to_start(),
                ])
                await event.answer("Похоже, у тебя нет подписчиков или ты накосячил с ник-неймом!",
                                   reply_markup=keyboard)


@start_router.callback_query(F.data == "re_roll_follow")
@user_permission_required
async def handle_re_roll_follow(event: CallbackQuery):
    await event.answer()
    try:
        new_follower = get_random_follower('myrzen_u')
    except ConnectionError:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[keyboards_button_bac_to_start()]])
        return await event.message.answer("На данный момент сервис перегружен.\n"
                                          "Попробуй другие функции бота или подожди пока все оживет ;)",
                                          reply_markup=keyboard)
    if new_follower:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_re_roll_follow(),
                                                         keyboards_button_bac_to_start()])
        await event.message.edit_text(f"Вот новый победитель: {new_follower}", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            keyboard_button_re_write_nickname(),
            keyboards_button_bac_to_start(),
        ])
        await event.message.edit_text("Похоже, у тебя нет подписчиков или ты накосячил с ник-неймом!",
                                      reply_markup=keyboard)

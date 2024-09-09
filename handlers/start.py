from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.chat_action import ChatActionSender
from create_bot import bot
from keyboards.keyboard_all import *
from request_twitch_api.api_request import *
from requests.exceptions import ConnectionError

start_router = Router()
user_nickname = {}
user_messages = {}


@start_router.message(CommandStart())
@start_router.callback_query(F.data == "back_to_start")
async def cmd_start(event: Message | CallbackQuery):
    message = None
    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message
    elif isinstance(event, Message):
        message = event
    if message:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            keyboard_button_random_followers(),
            keyboard_button_check_streamers()
        ])
        text_command = ('Приветствую!\n'
                        'Ниже весь доступный функционал бота!')
        if isinstance(event, Message):
            await message.answer(text_command,
                                 reply_markup=keyboard)
        else:
            await message.edit_text(text_command,
                                    reply_markup=keyboard)


@start_router.callback_query(F.data == "check_streamers")
async def handle_write_nickname(call: CallbackQuery):
    await call.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        keyboard_button_write_nickname(),
        keyboards_button_bac_to_start()
    ])
    sent_message = await call.message.edit_text('Напиши свой ник-нейм на твиче, чтобы увидеть своих стримеров!',
                                                reply_markup=keyboard)
    user_messages[call.message.from_user.id] = sent_message.message_id


@start_router.callback_query(F.data == "write_nickname")
async def handle_wait_write_nickname(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("Жду твой ник-нейм на твиче ⏳")
    user_nickname[call.from_user.id] = True


@start_router.message()
async def handle_get_list_streamers(message: Message):
    user_id = message.from_user.id
    if user_id in user_nickname and user_nickname[user_id] is True:
        nickname = message.text
        user_nickname[user_id] = nickname
        try:
            followed_streamers = get_followed(nickname)
        except ConnectionError:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[keyboards_button_bac_to_start()]])
            return await message.answer("На данный момент сервис поиска стримеров перегружен.\n"
                                        "Попробуй другие функции бота или подожди пока все оживет ;)",
                                        keyboard=keyboard)
        if followed_streamers:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                                                keyboard_button_list_streamers(status, name)
                                                                for name, status in followed_streamers.items()
                                                            ] + [keyboards_button_bac_to_start()])

            async with ChatActionSender(bot=bot, chat_id=user_id, action="typing"):
                await message.answer("Вот твои стримеры:", reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                keyboard_button_re_write_nickname(),
                keyboards_button_bac_to_start()
            ])
            await message.answer("Ты не подписан на стримеров или ты накосячил с ник-неймом!",
                                 reply_markup=keyboard)


@start_router.callback_query(F.data.startswith('streamer_'))
async def handle_streamer_click(call: CallbackQuery):
    await call.answer()
    streamer_name = call.data.replace('streamer_', '')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboards_button_bac_to_streamers()])
    await call.message.edit_text(f"Описание для стримера {streamer_name} пока не готово.",
                                 reply_markup=keyboard)


@start_router.callback_query(F.data == "back_to_streamers")
async def handle_back_to_streamers(call: CallbackQuery):
    user_id = call.from_user.id
    if user_id in user_nickname:
        nickname = user_nickname[user_id]
        followed_streamers = get_followed(nickname)

        if followed_streamers:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                                                keyboard_button_list_streamers(status, name)
                                                                for name, status in followed_streamers.items()
                                                            ] + [keyboards_button_bac_to_start()])

            await call.message.edit_text("Вот твои стримеры:", reply_markup=keyboard)
        else:
            await call.message.edit_text("Список стримеров пуст.")
    else:
        keyboards = InlineKeyboardMarkup(inline_keyboard=[
            keyboard_button_write_nickname(),
            keyboards_button_bac_to_start()
        ])
        await call.message.edit_text("Никнейм не найден, введите его снова.", reply_markup=keyboards)


@start_router.callback_query(F.data == "random_user")
async def handle_random_followers(call: CallbackQuery):
    await call.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        keyboard_button_write_nickname(),
        keyboards_button_bac_to_start()
    ])
    sent_message = await call.message.edit_text('Напиши свой ник-нейм на твиче, чтобы бот выбрал '
                                                'одного победителя из твоих подписчиков!',
                                                reply_markup=keyboard)
    user_messages[call.message.from_user.id] = sent_message.message_id


@start_router.message()
async def handle_get_random_followers(message: Message):
    user_id = message.from_user.id
    if user_id in user_nickname and user_nickname[user_id] is True:
        nickname = message.text
        user_nickname[user_id] = nickname
        try:
            followed_streamers = get_random_follower(nickname)
        except ConnectionError:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[keyboards_button_bac_to_start()]])
            return await message.answer("На данный момент сервис перегружен.\n"
                                        "Попробуй другие функции бота или подожди пока все оживет ;)",
                                        keyboard=keyboard)
        if followed_streamers:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboards_button_bac_to_start()])
            async with ChatActionSender(bot=bot, chat_id=user_id, action="typing"):
                await message.answer(f"Вот твой победитель: {followed_streamers}", reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                keyboard_button_re_write_nickname(),
                keyboards_button_bac_to_start()
            ])
            await message.answer("Похоже, у тебя нет подписчиков или ты накосячил с ник-неймом!",
                                 reply_markup=keyboard)
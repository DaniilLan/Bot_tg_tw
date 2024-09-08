from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.utils.chat_action import ChatActionSender
from create_bot import questions, bot
from keyboards.keyboard_all import *
from request_twitch_api.api_request import *

start_router = Router()
user_nickname = {}
user_messages = {}


@start_router.message(CommandStart())
@start_router.callback_query(F.data == "back_to_start")
async def cmd_start(event: Message | CallbackQuery):
    # Инициализируем переменную message
    message = None

    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message  # Присваиваем message только если это CallbackQuery
    elif isinstance(event, Message):
        message = event  # Присваиваем message, если это Message

    if message is not None:  # Проверяем, инициализирована ли переменная
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            keyboard_button_randon_followers(),
            keyboard_button_check_streamers()
        ])

        if message.text:  # Если это сообщение
            await message.answer('Приветствую!\n'
                                                 'Ниже весь доступный функционал бота!',
                                                 reply_markup=keyboard)
        else:  # Если это callback-запрос
            await message.edit_text('Приветствую!\n'
                                                    'Ниже весь доступный функционал бота!',
                                                    reply_markup=keyboard)


@start_router.callback_query(F.data == "check_streamers")
async def handle_write_nickname(call: CallbackQuery):
    await call.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        keyboard_button_write_nickname() +
        keyboards_button_bac_to_start()
    ])
    sent_message = await call.message.edit_text('Напиши СВОй ник-нейм на твиче, чтобы увидеть СВОих стримеров!',
                                                reply_markup=keyboard)
    user_messages[call.message.from_user.id] = sent_message.message_id  # Сохраняем ID сообщения


@start_router.callback_query(F.data == "write_nickname")
async def handle_wait_write_nickname(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("Жду твой ник-нейм...")
    user_nickname[call.from_user.id] = True


@start_router.message()
@start_router.callback_query(F.data == "back_to_streamers")
async def handle_get_list_streamers(message: Message):
    if message.from_user.id in user_nickname and user_nickname[message.from_user.id] is True:
        nickname = message.text
        user_nickname[message.from_user.id] = nickname  # Сохраняем ник-нейм
        followed_streamers = get_followed(nickname)
        if followed_streamers:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_list_streamers(status, name)
                                                             for name, status in followed_streamers.items()
                                                             ] + [keyboards_button_bac_to_start()])

            async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action="typing"):
                await message.answer("Вот твои стримеры:", reply_markup=keyboard)
        elif followed_streamers is ConnectionError:
            await message.answer("Сервис перегружен, подожди 5 минуток!")
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                keyboard_button_re_write_nickname()
            ])
            await message.answer("Ты не подписан на стримеров или ты накосячил с ник-неймом!",
                                 reply_markup=keyboard)
        del user_nickname[message.from_user.id]


@start_router.callback_query(F.data.startswith('streamer_'))
async def handle_streamer_click(call: CallbackQuery):
    await call.answer()
    streamer_name = call.data.replace('streamer_', '')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboards_button_bac_to_streamers()])
    await call.message.edit_text(f"Ну и хули ты тыкнул по {streamer_name} я еще там не дописал их описание",
                                 reply_markup=keyboard)


# @start_router.callback_query(F.data == "back_to_start")
# async def handle_back_to_start(call: CallbackQuery):
#     await call.answer()
#     original_message_id = user_messages.get(call.from_user.id)
#     if original_message_id:
#         # Редактируем текущее сообщение
#         keyboard = InlineKeyboardMarkup(inline_keyboard=[
#             keyboard_button_write_nickname()
#         ])
#         await call.message.edit_text('Напиши СВОй ник-нейм на твиче, чтобы увидеть СВОих стримеров!',
#                                      reply_markup=keyboard)

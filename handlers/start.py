import asyncio
import re
from aiogram import Router, F
from aiogram.dispatcher import router
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
from config import languages_flags
from db_handler.db_class import UserDatabase

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
        keyboard_button_check_streamers(),
        keyboard_button_notif_stream()
    ])
    text_command = ('Приветствую!\n'
                    'Ниже весь доступный функционал бота!')
    if isinstance(event, Message):
        await message.answer(text_command, reply_markup=keyboard)
    else:
        await message.edit_text(text_command, reply_markup=keyboard)


@start_router.callback_query(F.data == "request_permission")
@user_permission_required
async def handle_request_permission(event: CallbackQuery):
    await event.answer()
    db_user = UserDatabase(db_name="db_handler/tg_auth.db")
    user_id = event.from_user.id
    user_login = event.from_user.username
    check_add = db_user.add_record(user_id, user_login, "request_permission")
    if check_add is False:
        await event.message.edit_text("Запрос на предоставление доступа уже был отправлен!\n"
                                      "Ждите результата обработки.\n"
                                      "Обработка может занять до 24ч⏳")
    else:
        await event.message.edit_text("Запрос на предоставление доступа был отправлен!\n"
                                      "Ждите результата обработки.\n"
                                      "Обработка может занять до 24ч⏳")
    db_user.close()


@start_router.callback_query(F.data == "write_nickname")
@user_permission_required
async def handle_wait_write_nickname(event: CallbackQuery):
    await event.answer()
    await event.message.edit_text("Жду ник-нейм на твиче ⏳")
    user_nickname[event.from_user.id] = True


@start_router.callback_query(F.data == "add_notif_stream")
@user_permission_required
async def handle_wait_write_nickname(event: CallbackQuery):
    await event.answer()
    user_action[event.from_user.id] = 'add_notif_stream'
    await event.message.edit_text("Жду ник-нейм стримера на твиче ⏳")
    user_nickname[event.from_user.id] = True


@start_router.callback_query(F.data == "delete_notif_stream")
@user_permission_required
async def handle_wait_write_nickname(event: CallbackQuery):
    await event.answer()
    user_action[event.from_user.id] = 'delete_notif_stream'
    await event.message.edit_text("Жду ник-нейм стримера на твиче для удаления из уведомлений ⏳")
    user_nickname[event.from_user.id] = True


@start_router.callback_query(F.data.startswith('streamer_'))
@user_permission_required
async def handle_streamer_click(event: CallbackQuery):
    await event.answer()
    match = re.match(r'^streamer_(.+?)_(🔴|⚫️)$', event.data)
    print(match)
    if not match:
        await event.answer("Некорректные данные", show_alert=True)
        return

    streamer_name = match.group(1)
    life_status = match.group(2)
    streamers = get_info_stream(streamer_name)[0]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_open_channel(streamer_name),
                                                     keyboards_button_bac_to_streamers()])
    if not streamers['data']:
        await event.message.edit_text(f'Стример {streamer_name} офлайн, позже добавлю описание его последней трансляции.', reply_markup=keyboard)
    else:
        info_streamer = streamers['data'][0]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_open_channel(streamer_name),
                                                         keyboards_button_bac_to_streamers()])
        await event.message.delete()
        lang_tag = info_streamer['language']
        flag = languages_flags.get(lang_tag, '')
        text = (f"{life_status} <b>{streamer_name}</b>\n"
                f"Описание трансляции стримера:\n"
                f"\n"
                f"{f'👁 <b>Количество зрителей: {info_streamer['viewer_count']}\n\n</b>' if life_status == '🔴' else ''}"
                f"👅 <b>Язык трансляции: {flag}\n"
                f"\n"
                f"🎮 Категория {'текущей' if life_status == '🔴' else 'прошлой'} трансляции: {info_streamer['game_name']}\n"
                f"\n"
                f"📝 Описание {'текущей' if life_status == '🔴' else 'прошлой'} трансляции: {info_streamer['title']}\n"
                f"\n"
                f"⁉️ Теги {'текущей' if life_status == '🔴' else 'прошлой'} трансляции: {'➕'.join(info_streamer['tags'])}\n"
                f"\n"
                f"⚠️ Стрим {'c возрастным ограничением' if info_streamer['is_mature'] is False else 'без возрастного ограничения'}!</b>")

        await bot.send_photo(
            chat_id=event.message.chat.id,
            photo=get_user_pf(streamer_name),
            reply_markup=keyboard,
            caption=text,
            parse_mode='HTML'
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
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[keyboard_button_re_write_nickname()],
                                                             [keyboards_button_bac_to_start()]])
            if event.message.content_type == 'text':
                await event.message.edit_text("Список стримеров пуст.", reply_markup=keyboard)
            else:
                await event.message.delete()
                await event.message.answer("Список стримеров пуст.", reply_markup=keyboard)
    else:
        keyboards = InlineKeyboardMarkup(inline_keyboard=[
            keyboards_button_bac_to_start()
        ])
        if event.message.content_type == 'text':
            await event.message.edit_text("Никнейм не найден.", reply_markup=keyboards)
        else:
            await event.message.delete()
            await event.message.answer("Никнейм не найден.", reply_markup=keyboards)


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


@start_router.callback_query(F.data == "notif_stream")
@user_permission_required
async def handle_request_permission(event: CallbackQuery):
    await event.answer()
    db_user = UserDatabase(db_name="db_handler/tg_auth.db")
    id_user = event.from_user.id
    my_streamers = db_user.get_name_streamers(id_user=id_user)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_add_notif(),
                                                     keyboards_button_bac_to_start()])
    if not my_streamers:
        sent_message = await event.message.edit_text(f'🔔\n'
                                                     f'<b>Ты будешь получать уведомления о начале трансляции стримера(ов):</b>\n\n'
                                                     f'<b>➡️ Список стримеров пуст!\n Нажми кнопку "Добавить '
                                                     f'стримера", что бы получать уведомления о начале его '
                                                     f'трансялции.</b>', reply_markup=keyboard,
                                                     parse_mode="HTML")
        user_messages[event.message.from_user.id] = sent_message.message_id
        db_user.close()
    else:
        my_streamers = [streamer[0] for streamer in my_streamers]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_add_notif(),
                                                         keyboard_button_delete_notif(),
                                                         keyboards_button_bac_to_start()])
        sent_message = await event.message.edit_text(f'🔔\n'
                                      f'<b>Ты будешь получать уведомления о начале трансляции стримера(ов):</b>\n\n'
                                      f'<b>➡️ {"\n➡️ ".join(my_streamers)}</b>', reply_markup=keyboard, parse_mode="HTML")
        user_messages[event.message.from_user.id] = sent_message.message_id
        db_user.close()


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
            if followed_streamers:
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
            if followed_streamers:
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
        elif action == 'add_notif_stream':
            id_user = event.from_user.id
            name_streamer = event.text
            info = get_info_stream(name_streamer)
            if info[1] == 400:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_re_write_notif(),
                                                                 keyboards_button_bac_to_start()])
                await event.answer(f"Похоже, такого стримера нету или ты накосячил с ник-неймом!", reply_markup=keyboard)
            else:
                db_user = UserDatabase(db_name="db_handler/tg_auth.db")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_bac_to_notif_stream(),
                                                                 keyboards_button_bac_to_start()])
                add_user = db_user.add_user_for_notif(id_user, name_streamer)
                if add_user:
                    await event.answer(f"Стример {name_streamer} добавлен в ваши уведомления!", reply_markup=keyboard)
                    db_user.close()
                else:
                    if add_user is False:
                        await event.answer(f"Похоже ты уже добавил стримера {name_streamer} для уведомлений.", reply_markup=keyboard)
                    else:
                        await event.answer(f"Запрос не прошел в базе данных.", reply_markup=keyboard)
                    db_user.close()
        elif action == 'delete_notif_stream':
            id_user = event.from_user.id
            name_streamer = event.text
            db_user = UserDatabase(db_name="db_handler/tg_auth.db")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_bac_to_notif_stream(),
                                                             keyboards_button_bac_to_start()])
            if db_user.delete_streamer(name_streamer, id_user):
                keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_bac_to_notif_stream(),
                                                                 keyboards_button_bac_to_start()])
                await event.answer(f"Стример {name_streamer} удален из твоего списка уведомлений!",
                                   reply_markup=keyboard)
            else:
                await event.answer(f"Похоже ты ошибся с ник-неймом или этого стрмиера нет в твоих уведомлениях.",
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

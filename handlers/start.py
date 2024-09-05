from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import asyncio
from aiogram.utils.chat_action import ChatActionSender

import create_bot
from keyboards.inline_kbs import create_qst_inline_kb
from create_bot import questions, bot, dp
from request_twitch_api.get_list_folow import get_followed
start_router = Router()


@start_router.message(CommandStart())
async def cmd_start_2(message: Message):
    await message.answer('Список стримеров онлай!', reply_markup=create_qst_inline_kb(questions))


@start_router.callback_query(F.data.startswith('qst_'))
async def cmd_start(call: CallbackQuery):
    await call.answer()
    qst_id = int(call.data.replace('qst_', ''))
    msg_text = f''
    if get_followed('iLame'):
        for name, status in get_followed('a_hyena_dobr').items():
            msg_text += f"{status}: {name}\n"
    async with ChatActionSender(bot=bot, chat_id=call.from_user.id, action="typing"):
        questions_1 = questions.copy()
        questions_1.pop(qst_id, None)
        await call.message.edit_text(msg_text, reply_markup=create_qst_inline_kb(questions_1))

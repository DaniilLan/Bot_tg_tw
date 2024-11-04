from aiogram import Bot, Dispatcher, types
import asyncio


API_TOKEN = '5355724378:AAHJWzRJoKk0Fa_uYSuABBP1itywYeeak3g'  # Замените на токен вашего бота

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик, который выведет ID группы в консоль
@dp.message()
async def get_chat_id(message: types.Message):
    chat_id = message.chat.id
    print(f"ID группы: {chat_id}")
    await message.answer(f"ID группы: {chat_id}")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
import asyncio
from telethon import TelegramClient, events

# Определение учетных данных API и имен сессий для двух ботов Telegram
api_id = 22269966
api_hash = '507a1cc92759a4e75263263ee5ac1e9e'
session_name_1 = 'main_bot'
bot_token_1 = '7779869736:AAF-OEkppmp2cy1CVGRzBswD98pXTzMvqsA'
session_name_2 = 'assistant_bot'
bot_token_2 = '7296691653:AAGM7hn0C0vlG9_2tYR6-1BS6x1sfHvRrTc'

# Создание двух клиентов Telegram
client1 = TelegramClient(session_name_1, api_id, api_hash).start(bot_token=bot_token_1)
client2 = TelegramClient(session_name_2, api_id, api_hash).start(bot_token=bot_token_2)

# ID группы, где будут общаться боты и пользователь
group_chat_id = -1002318408686
# ID пользователя, отправившего запрос
user_id = 1022548979

@client1.on(events.NewMessage)
async def main_bot_handler(event):
    if event.is_private and event.sender_id == user_id:
        # Получаем текст сообщения с примером и отправляем его в группу для решения
        math_expression = event.raw_text
        await client1.send_message(group_chat_id, f"Помоги решить: {math_expression}")

@client2.on(events.NewMessage)
async def assistant_bot_handler(event):
    if event.is_group and event.chat_id == group_chat_id:
        message_text = event.raw_text
        # Проверяем, что сообщение отправлено первым ботом
        sender = await client1.get_me()  # Используем await для получения информации о боте
        if message_text.startswith("Помоги решить:"):
            # Получаем математическое выражение и решаем его
            math_expression = message_text.replace("Помоги решить:", "").strip()
            try:
                answer = eval(math_expression)
                await asyncio.sleep(1)  # Небольшая задержка
                await client2.send_message(group_chat_id, f"Ответ: {answer}")
            except Exception as e:
                await client2.send_message(group_chat_id, f"Не удалось решить: {e}")

@client1.on(events.NewMessage)
async def main_bot_forward_response(event):
    if event.is_group and event.chat_id == group_chat_id:
        if event.raw_text.startswith("Ответ:"):
            # Пересылаем ответ из группы в личные сообщения пользователя
            await client1.send_message(user_id, event.raw_text)

# Функция для параллельного запуска клиентов
async def main():
    await asyncio.gather(
        client1.run_until_disconnected(),
        client2.run_until_disconnected()
    )

# Запуск обоих клиентов
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

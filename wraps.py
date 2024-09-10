from keyboards.keyboard_all import *
from db_handler.db_class import *
from functools import wraps


async def check_user(event, user_id=None):
    db_user = UserDatabase(db_name="db_handler/tg_auth.db")
    user_id = event.from_user.id
    tg_user = db_user.get_user(user_id)
    if tg_user is None:
        if isinstance(event, Message):
            await event.answer("В доступе отказано.")
            return False
        elif isinstance(event, CallbackQuery):
            await event.message.edit_text("В доступе отказано.")
            return False
    else:
        return True


def user_permission_required(func):
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        permission = await check_user(event)
        if not permission:
            return  # Если пользователь не авторизован, завершаем выполнение функции
        return await func(event, *args, **kwargs)
    return wrapper

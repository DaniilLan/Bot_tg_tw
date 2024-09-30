from keyboards.keyboard_all import *
from db_handler.db_class import *
from functools import wraps


async def check_user(event, user_id=None):
    db_user = UserDatabase()
    user_id = event.from_user.id
    user_login = event.from_user.username
    tg_user = db_user.get_user(user_id)
    db_user.close()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_button_request_permission()]) # callback_data="request_permission"
    print(user_login)
    print(user_id)
    if tg_user is None:
        if isinstance(event, Message):
            await event.answer("В доступе отказано.", reply_markup=keyboard)
            return False
        elif isinstance(event, CallbackQuery):
            await event.message.edit_text("В доступе отказано.",  reply_markup=keyboard)
            return False
    else:
        return True


def user_permission_required(func):
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        permission = await check_user(event)
        if not permission:
            return
        return await func(event, *args, **kwargs)
    return wrapper

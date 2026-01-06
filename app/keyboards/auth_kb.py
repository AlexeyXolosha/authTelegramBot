from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_auth_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton (
        text="📱 Подтвердить номер телефона", 
        request_contact=True
    ))

    return builder.as_markup(
        resize_keyboard=True, 
        one_time_keyboard=True
    )
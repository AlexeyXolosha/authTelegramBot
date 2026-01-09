from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.utils.text import MESSAGES

def get_auth_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    button_text = MESSAGES.get(lang, MESSAGES["ru"])["auth_button"]

    builder.row(KeyboardButton(
        text=button_text, 
        request_contact=True 
    ))

    return builder.as_markup(
        resize_keyboard=True, 
        one_time_keyboard=True
    )
import time
import asyncio
import urllib.parse
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from app.states.auth_states import AuthStates
from app.keyboards.auth_kb import get_auth_keyboard
from app.utils.text import MESSAGES
from app.services.api_client import authorize_user_in_laravel
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

AUTH_TIMEOUT = 300 

@router.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject, state: FSMContext):
    args = command.args
    if args:
        parts = args.split("_")
        if len(parts) == 2:
            auth_token, lang = parts

            current_lang = lang if lang in MESSAGES else "ru"

            start_time = int(time.time())

            await state.update_data(
                saved_token=auth_token,
                user_lang=current_lang,
                auth_start_time=start_time
            )

            await state.set_state(AuthStates.waiting_for_contact)
            
            text = MESSAGES[current_lang]["welcome"]
            await message.answer(text, reply_markup=get_auth_keyboard(lang=current_lang))
            return
    
    await message.answer(MESSAGES["ru"]["bad_link"])


@router.message(AuthStates.waiting_for_contact, F.contact) 
async def handle_contact(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("user_lang", "ru")
    start_time = user_data.get("auth_start_time", 0)
    
    current_time = int(time.time())
    elapsed_time = current_time - start_time

    if elapsed_time > AUTH_TIMEOUT:
        await state.clear()
        await message.answer(MESSAGES[lang]["bad_link"], reply_markup=types.ReplyKeyboardRemove())
        return

    if message.contact.user_id != message.from_user.id:
        await message.answer(MESSAGES[lang]["wrong_contact"])
        return
    
    await message.answer(MESSAGES[lang]["processing"])

    response_data = await authorize_user_in_laravel(
        user_data=user_data, 
        contact=message.contact, 
        from_user=message.from_user
    )

    token = response_data.get("data", {}).get("token") if isinstance(response_data, dict) else None
    
    if token:
        remaining_time = AUTH_TIMEOUT - elapsed_time
        
        if remaining_time <= 5:
            await state.clear()
            await message.answer(MESSAGES[lang]["bad_link"])
            return

        safe_token = urllib.parse.quote(token)
        redirect_url = f"https://rdrxes.ru/redirect.html?token={safe_token}"
        
        btn_text = MESSAGES[lang]["open_app_btn"]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=btn_text, url=redirect_url)]
        ])

        final_text = (
            f"{MESSAGES[lang]['success']}\n\n"
            f"{MESSAGES[lang]['redirect_instruction']}\n"
            f"{MESSAGES[lang]['expire_note']}"
        )

        sent_msg = await message.answer(
            final_text, 
            reply_markup=keyboard, 
            parse_mode="HTML"
        )

        async def expire_button_task(msg: types.Message, delay: int):
            await asyncio.sleep(delay)
            try:
                new_text = msg.html_text + f"\n\n❌ <b>Срок действия истек.</b>"
                await msg.edit_text(new_text, reply_markup=None, parse_mode="HTML")
                await state.clear() 
            except Exception:
                pass

        asyncio.create_task(expire_button_task(sent_msg, remaining_time))

    else:
        await message.answer(MESSAGES[lang]["error"])
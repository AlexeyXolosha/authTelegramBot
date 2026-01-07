from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from app.states.auth_states import AuthStates
from app.keyboards.auth_kb import get_auth_keyboard
from app.utils.text import MESSAGES

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject, state: FSMContext):
    args = command.args

    if args:
        parts = args.split("_")
        if len(parts) == 3:
            auth_token, link_phone, lang = parts
            current_lang = lang if lang in MESSAGES else "ru"

            await state.update_data(
                saved_token=auth_token,
                phone_from_link=link_phone,
                user_lang=current_lang 
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
    phone_from_link = user_data.get("phone_from_link")
    phone_from_tg = message.contact.phone_number

    if message.contact.user_id != message.from_user.id:
        await message.answer(MESSAGES[lang]["wrong_contact"])
        return
    
    def clean_phone(p):
        return ''.join(filter(str.isdigit, str(p)))
    
    if clean_phone(phone_from_tg) != clean_phone(phone_from_link):
        await message.answer(MESSAGES[lang]["phone_mismatch"])
        return
    
    print(f"УСПЕХ: Номера совпали ({clean_phone(phone_from_tg)}). Отправляем в Laravel.")
    
    await state.clear()
    await message.answer(MESSAGES[lang]["processing"], reply_markup=types.ReplyKeyboardRemove())
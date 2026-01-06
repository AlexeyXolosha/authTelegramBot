from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from app.states.auth_states import AuthStates
from app.keyboards.auth_kb import get_auth_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject, state: FSMContext):
    otp = command.args

    if otp and otp.startswith("verify_"):
        clean_otp = otp.replace("verify_", "")
        await state.update_data(saved_otp=clean_otp)
        
        await state.set_state(AuthStates.waiting_for_contact)
        await message.answer(
            "Нажмите кнопку ниже, чтобы отправить номер телефона для верификации.", 
            reply_markup=get_auth_keyboard()
        )
    else: 
        await message.answer("Пожалуйста, зайдите через сайт (ссылка должна содержать код верификации).")


@router.message(AuthStates.waiting_for_contact, F.contact) 
async def handle_contact(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    otp = user_data.get("saved_otp")
    
    phone = message.contact.phone_number
    
    print(f"Отправляем в Laravel: {phone} и {otp}")
    
    await state.clear()
    await message.answer("Данные приняты. Проверяем в системе...", reply_markup=types.ReplyKeyboardRemove())
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
import asyncpg
from loader import dp, db, bot
from data.config import ADMINS
from states.admin import AdminState
from aiogram.dispatcher import FSMContext

@dp.message_handler(text="Userga xabar yuborish", user_id=ADMINS)
async def send_message_to_user(message: types.Message):
    await message.answer("User ID sini yuboring")
    await AdminState.message_to_user.set()
    
@dp.message_handler(state=AdminState.message_to_user, user_id=ADMINS)
async def send_message_to_user_by_id(message: types.Message, state=FSMContext):
    user_id = message.text.strip()
    
    await state.update_data({
        "user_id": user_id
    })
    
    await message.answer("Userga yubormoqchi bo'lgan kitob linkini yuboring")
    await AdminState.message_to_user_file.set()
    
    
@dp.message_handler(state=AdminState.message_to_user_file, user_id=ADMINS)
async def send_message(message: types.Message, state=FSMContext):
    book_link = message.text
    data = await state.get_data()
    user_id = data.get("user_id", None)
    user = await db.select_user(telegram_id=int(user_id))
    
    try:
        await bot.send_document(chat_id=user_id, document=book_link, caption="SIZ QIDIRGAN KITOB\n\n@mobilkutubxona_bot")
        await message.answer("Xabar yuborildi")
        await state.finish()
    except Exception as e:
        await message.answer(f"Xatolik: {e}")
        await state.finish()

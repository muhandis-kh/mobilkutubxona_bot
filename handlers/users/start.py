from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
import asyncpg
from loader import dp, db, bot
from data.config import ADMINS
from keyboards.default.default import random_book

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    try:
        user = await db.add_user(telegram_id=message.from_user.id,
                                 full_name=message.from_user.full_name,
                                 username=message.from_user.username,
                                 )
        # ADMINGA xabar beramiz
        count = await db.count_users()
        msg = f"{user[1]} bazaga qo'shildi.\nBazada {count} ta foydalanuvchi bor."
        await bot.send_message(chat_id=ADMINS[0], text=msg)
        
    except asyncpg.exceptions.UniqueViolationError:
        pass
    await message.answer(f"Assalomu aleykum, {message.from_user.full_name}! 👋 Xush kelibsiz.\n\n🔎 Izlagan kitobingiz nomini imlo qoidalarga amal qilgan holda, lotin alifbosida kiriting.", reply_markup=random_book)
    
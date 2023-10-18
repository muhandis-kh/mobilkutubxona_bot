from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
import asyncpg
import random
from loader import dp, db, bot
from data.config import ADMINS
from keyboards.default.default import random_book
import json
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
    await message.answer(f"Salom, {message.from_user.full_name}!", reply_markup=random_book)
    
@dp.message_handler(commands=['library'])
async def myCommand(message: types.Message):
    user_telegram_id = message.from_user.id
    
    user_books = await db.get_favorite_books(telegram_id=user_telegram_id)

    if user_books[0]:
        user_books = json.loads(user_books[0])
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        print(user_books)
        for key, value in user_books.items():
            text = f"{key}"
            print(value)
            button = types.InlineKeyboardButton(text=text, callback_data=f"my_books__{value}")
            keyboard.insert(button)
        
        await message.answer("Sizning kutubxonangizda quyidagi kitoblar mavjud: ", reply_markup=keyboard)
    else:
        await message.answer("Sizning kutubxonangizda hali kitob yo'q")
            
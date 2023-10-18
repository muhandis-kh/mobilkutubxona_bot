from loader import dp, db
from aiogram import types

@dp.message_handler(commands=['library'])
async def myCommand(message: types.Message):
    print(message)
    user_telegram_id = message.from_user.id
    
    user_books = await db.get_favorite_books(telegram_id=user_telegram_id)
    print(user_books)
from loader import dp, db
from aiogram import types
import json

@dp.message_handler(commands=['library'])
async def myCommand(message: types.Message):
    user_telegram_id = message.from_user.id
    
    user_books = await db.get_favorite_books(telegram_id=user_telegram_id)

    if user_books[0]:
        user_books = json.loads(user_books[0])
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for key, value in user_books.items():
            text = f"{key}"
            button = types.InlineKeyboardButton(text=text, callback_data=f"my_books__{value}")
            keyboard.insert(button)
        
        await message.answer("Sizning kutubxonangizda quyidagi kitoblar mavjud: ", reply_markup=keyboard)
    else:
        await message.answer("Sizning kutubxonangizda hali kitob yo'q")
from aiogram import types
from loader import dp, db
from .functions import make_query
from random import randrange

@dp.message_handler(text="🎲 Tasodifiy kitob", state=None)
async def send_random_book(message: types.Message):
    # Bazaga so'rovni kamaytirish uchun va tezlikni oshirish uchun databaza dagi kitoblar soni local holatda kiritib qo'yildi
        link = "http://mlibrary.up.railway.app/api/file-book-api/"
    # count = make_query(link=link)
    # if count:
        bookMenu = types.InlineKeyboardMarkup(row_width=2)
        random = randrange(456, 83715)
        link = f"{link.split('?')[0]}{random}"
        random_book = make_query(link=link)
        if random_book:
            favorites_btn = types.InlineKeyboardButton(text="❤️/💔", callback_data=f"favorites_btn__{random_book['file_link']}")
            delete_mgs_btn = types.InlineKeyboardButton(text="❌", callback_data="delete_msg")
            bookMenu.insert(favorites_btn)
            bookMenu.insert(delete_mgs_btn)
            await message.answer_document(caption=random_book['description'], document=random_book['file_link'], reply_markup=bookMenu)
        else:
            await message.answer(text="😥 Iltimos qayta urunib ko'ring")

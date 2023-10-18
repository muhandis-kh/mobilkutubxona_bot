from aiogram import types
from loader import dp

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('my_books__'))
async def my_books_sender(callback_query: types.CallbackQuery):
    bookMenu = types.InlineKeyboardMarkup(row_width=2)
    book_link = callback_query.data.split("__")[1]
    favorites_btn = types.InlineKeyboardButton(text="❤️/💔", callback_data=f"favorites_btn__{book_link}")
    delete_mgs_btn = types.InlineKeyboardButton(text="❌", callback_data="delete_msg")
    bookMenu.insert(favorites_btn)
    bookMenu.insert(delete_mgs_btn)
    
    await callback_query.message.answer_document(document=book_link, reply_markup=bookMenu)
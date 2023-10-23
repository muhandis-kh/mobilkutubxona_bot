from aiogram import types

from loader import dp, db, bot
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
import json
from aiogram.dispatcher import FSMContext
from .functions import get_keyboards, make_query, keyboard
from pprint import pprint
from data.config import ADMINS

# so'rovlar yuborish uchun API shablon linki
link = "http://mlibrary.up.railway.app/api/file-book-api/?"

#Xabarlarni yangilash uchun funksiya
async def update_message(message: types.Message, new_value: str, keyboard: json):
    with suppress(MessageNotModified):
      await message.edit_text(text=new_value, reply_markup=keyboard)  



# Funksiyalardan      
data = tuple

@dp.message_handler(state=None)
async def search(message: types.Message, state=FSMContext):

    # if message.text != "🎲 Tasodifiy kitob":    
    data = get_keyboards(message.text)
    text = data[0]
    status_code = data[1]
    try:
        keyboard = data[2]
        await state.update_data(data[3])
    except Exception as e:
        msg = f"Ma'lumotlarni olishdada xatolik: {e}"
        await bot.send_message(chat_id=ADMINS[0], text=msg)

    
    if status_code == 200:
        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer(text)
            

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('book_'))
async def process_book_button(callback_query: types.CallbackQuery, state=FSMContext):
    book_link = callback_query.data.split('__')[1]
    data = await state.get_data()
    bookMenu = types.InlineKeyboardMarkup(row_width=2)
    if data:
        for obj in data['results']:
            if obj['file_link'] == book_link:
                favorites_btn = types.InlineKeyboardButton(text="❤️/💔", callback_data=f"favorites_btn__{book_link}")
                delete_mgs_btn = types.InlineKeyboardButton(text="❌", callback_data="delete_msg")
                # audio_format = types.InlineKeyboardButton(text="🔉 Kitobning audio formatini qidir", callback_data="delete_msg")
                bookMenu.insert(favorites_btn)
                bookMenu.insert(delete_mgs_btn)
                try:
                    await callback_query.message.answer_document(caption=obj['description'].replace('\n', ''), document=book_link, reply_markup=bookMenu)
                except Exception as e:
                    msg = f"Kitobni yuborishda xatolik: {e}"
                    await bot.send_message(chat_id=ADMINS[0], text=msg)
                                
            else:
                print("Obj datada yo'q")        
        await bot.answer_callback_query(callback_query.id)
    else:
        print("Data yo'q")
        

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('next_page_'))
async def change_page(query: types.CallbackQuery, state=FSMContext):
    if query.data.split('__')[1] == '':
        await query.answer(text="Sahifalar tugadi")
    
    else:
        
        next_page_link = link + query.data.split('__')[1]
        data = make_query(next_page_link)
        await state.update_data(data)
        keyboards = keyboard(data)
        try:
            await update_message(message=query.message, new_value=keyboards[1], keyboard=keyboards[0] )
        except  Exception as e:
            msg = f"Xabarni yangilashda xatolik: {e}"
            await bot.send_message(chat_id=ADMINS[0], text=msg)
            
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('prev_page_'))
async def change_page(query: types.CallbackQuery, state=FSMContext):

    if query.data.split('__')[1] == "":
        await query.answer(text="Siz allaqachon birinchi sahifadasiz!")
    else:
        prev_page_link = link + query.data.split('__')[1]
        data = make_query(prev_page_link)
        await state.update_data(data)
        keyboards = keyboard(data)
        
        await update_message(message=query.message, new_value=keyboards[1], keyboard=keyboards[0])
        
@dp.callback_query_handler(text_contains="favorites_btn")
async def add_rm_fv_books(callback_query: types.CallbackQuery, state=FSMContext):
    user_telegram_id = callback_query.from_user.id
    document_filename = callback_query.message.document.file_name
    document_link = callback_query.data.split('__')[1]
    
    user_books = await db.get_favorite_books(telegram_id=user_telegram_id)
    
    favorite_books = {document_filename : document_link}
    if user_books['favorite_books']:
        user_books = json.loads(user_books[0])
        if not(document_filename in user_books):
            user_books.update({document_filename: document_link})
            await db.update_user_favorite_books(favorite_books=json.dumps(user_books), telegram_id=user_telegram_id)
            await callback_query.answer(text="Kitob sevimlilar ro'yhatiga qo'shildi")
        else:
            user_books.pop(document_filename)
            await db.update_user_favorite_books(favorite_books=json.dumps(user_books), telegram_id=user_telegram_id)
            await callback_query.answer(text="Kitob sevimlilar ro'yhatidan o'chirildi")
            
            
    else:
        user_books = dict(user_books)
        user_books['favorite_books'] = favorite_books
        await db.update_user_favorite_books(favorite_books=json.dumps(user_books['favorite_books']), telegram_id=user_telegram_id)


@dp.callback_query_handler(text_contains="delete_msg")
async def delete_msg(callback_query: types.CallbackQuery, state=FSMContext):
    message = callback_query.message
    
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        msg = f"Xabarni o'chirib yuborishda xatolik: {e}"
        await bot.send_message(chat_id=ADMINS[0], text=msg)
        
    # await call.answer(cache_time=60)
  
  
# Audio kitoblar apiga qo'shilganda qo'shiladigan bo'lim  
# @dp.callback_query_handler(text_contains="🔉 Kitobning audio formatini qidir")
# async def delete_msg(callback_query: types.CallbackQuery, state=FSMContext):
#     callback_data = callback_query
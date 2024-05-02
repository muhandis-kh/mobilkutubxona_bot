from aiogram import types

from loader import dp, db, bot
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
import json
from aiogram.dispatcher import FSMContext
from .functions import get_data, make_query, get_keyboards_and_text
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


# Foydalanuvchidan text ko'rinishida habar kelganida uni funksiyalar orqali apiga yuborish va variantlarni yoki kitob topilmagani haqida habar yuborish uchun funksiya
@dp.message_handler(state=None)
async def search(message: types.Message, state=FSMContext):

    
    # if message.text != "🎲 Tasodifiy kitob":    
        data = get_data(message.text)
        msg = f"<b>TOPILDI !!!</b>\n\nQidirilgan kitob: {message.text}\nQidirgan foydalanuvchi: {message.from_user.full_name} (<a href='tg://user?id={message.from_user.id}'>{('@'+ message.from_user.username) if message.from_user.username else (message.from_user.first_name)}</a>)"
        await bot.send_message(chat_id=ADMINS[0], text=msg)

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
            msg = f"<b>TOPILMADI !!!</b>\n\nQidirilgan kitob: {message.text}\nQidirgan foydalanuvchi: {message.from_user.full_name} (<a href='tg://user?id={message.from_user.id}'>{('@'+ message.from_user.username) if message.from_user.username else (message.from_user.first_name)}</a>)"
            await bot.send_message(chat_id=ADMINS[0], text=msg)

            

# Foydalanuvchidan kelgan 'book_' orqali boshlanadigan query.datani ushlab olish uchun funksiya
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('book_'))
async def process_book_button(callback_query: types.CallbackQuery, state=FSMContext):
    # Kelgan datadan kitob telegram linkini olish
    book_link = callback_query.data.split('__')[1]
    # Kitob ma'lumotlarini olish uchun
    data = await state.get_data()
    # bookMenu nomi ostida tugmalar to'plami
    bookMenu = types.InlineKeyboardMarkup(row_width=2)

    
    if data:
        for obj in data['results']:
            # Agar kelgan kitob linki olingan ma'lumotlardan bo'lsa kitob yuboriladi
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
                pass
                # print("Obj datada yo'q")        
        await bot.answer_callback_query(callback_query.id)
    else:
        print("Data yo'q")
        

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('next_page_'))
async def change_page(query: types.CallbackQuery, state=FSMContext):
    # next_page bilan boshlanuvchi link yo'q bo'lsa ushbu xabar chiqadi
    if query.data.split('__')[1] == '':
        await query.answer(text="Sahifalar tugadi")
    
    # Bo'sh bo'lmasa linkga so'rov yuborib kelgan ma'lumotlar foydalanuvchiga ko'rsatiladi
    else:
        next_page_link = link + query.data.split('__')[1]
        data = make_query(next_page_link)
        await state.update_data(data)
        keyboards_and_text = get_keyboards_and_text(data)
        try:
            await update_message(message=query.message, new_value=keyboards_and_text[1], keyboard=keyboards_and_text[0] )
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
        keyboards_and_text = get_keyboards_and_text(data)
        
        await update_message(message=query.message, new_value=keyboards_and_text[1], keyboard=keyboards_and_text[0])
        
        
# Foydalanuvchi kutubxonasiga kitobni qo'shish uchun ishlatadigan tugmani bosganida ishlovchi funksiya
@dp.callback_query_handler(text_contains="favorites_btn")
async def add_rm_fv_books(callback_query: types.CallbackQuery, state=FSMContext):
    user_telegram_id = callback_query.from_user.id
    document_filename = callback_query.message.document.file_name
    document_link = callback_query.data.split('__')[1]
    
    # Foydalanuvchi tanlagan kitoblar ro'yhati bazada saqlangan shu ma'lumotlar olindi
    user_books = await db.get_favorite_books(telegram_id=user_telegram_id)
    
    # Yangi kitob Obyekt ko'rinishida saqlandi
    favorite_books = {document_filename : document_link}
    
    # Foydalanuvchi tanlagan kitoblar ro'yhati bo'sh yoki bo'sh emasligini tekshiradi
    if user_books['favorite_books']:
        # Kitoblar ro'hatini json typedan python obj type ga o'girib oldi
        user_books = json.loads(user_books[0])
        
        # Yangi tanlangan kitob foydalanuvchi kutubxonasida bor yoki yo'qligini tekshiradi. 
        # Agar kitob foydalanuvchi kutubxonasida bo'lmasa kitob kutubxonaga qo'shiladi, agar bo'lsa kutubxonadan olib tashlanadi
        if not(document_filename in user_books):
            user_books.update({document_filename: document_link})
            await db.update_user_favorite_books(favorite_books=json.dumps(user_books), telegram_id=user_telegram_id)
            await callback_query.answer(text="Kitob sevimlilar ro'yhatiga qo'shildi")
        else:
            user_books.pop(document_filename)
            await db.update_user_favorite_books(favorite_books=json.dumps(user_books), telegram_id=user_telegram_id)
            await callback_query.answer(text="Kitob sevimlilar ro'yhatidan o'chirildi")
            
    # Foydalanuvchi kutubxonasi bo'sh bo'lsa yangi kitob kutubxonaga qo'shiladi   
    else:
        user_books = dict(user_books)
        user_books['favorite_books'] = favorite_books
        await db.update_user_favorite_books(favorite_books=json.dumps(user_books['favorite_books']), telegram_id=user_telegram_id)


# Foydalanuvchiga yuborilgan kitob faylini foydalanuvchi o'chirib yuborish tugmasini bosganida ishlovchi funksiya
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
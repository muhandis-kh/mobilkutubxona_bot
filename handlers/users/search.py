from aiogram import types

from loader import dp, db, bot
import requests
from urllib.parse import quote
from pprint import pprint
from data.config import TOKEN
import random
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
import json
from aiogram.dispatcher import FSMContext
# from keyboards.inline.inline import bookMenu
import json
# from psycopg2.extras import Json

link = "http://mlibrary.up.railway.app/api/file-book-api/?"

def make_query(link):
    token = TOKEN
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.get(link, headers=headers)
    except Exception as e:
        print(e)
        return False
        
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error code: {response.status_code}")

def get_books_data(query):
    encoded_query = quote(query)


    # URL
    api_url = f"https://mlibrary.up.railway.app/api/file-book-api/?search={encoded_query}"

    return make_query(api_url)


def keyboard(books_data):
    books = ["📔", "📕", "📖", "📗", "📘", "📙", "📚", "📑", "🔖", "🧾"]
    rows = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            8: 4,
            10: 5
        }
    
    try:
        keyboard = types.InlineKeyboardMarkup(row_width=rows[len(books_data['results'])])
    except KeyError:
        keyboard = types.InlineKeyboardMarkup(row_width=len(books_data['results']))
        
    
    
    if books_data['next']:
        number_page = books_data['next'].split("?")[1][5:6]
        try:
            number_page = int(number_page)
            if number_page > 2:
                text = f"Natijalar {number_page-2}1-{number_page-1}0 {books_data['count']} tadan\n\n"
            else:
                text = f"Natijalar 1-10 {books_data['count']} tadan\n\n"
        except Exception as e:
            print("Error ", e)
    
    elif books_data['previous']:
        number_page = books_data['previous'].split("?")[1][5:6]
        try:
            number_page = int(number_page)
            if number_page > 1:
                if books_data['next']:
                    text = f"Natijalar {number_page+1}1-{number_page+2}0 {books_data['count']} tadan\n\n"
                else:
                    text = f"Natijalar {number_page}1-{books_data['count']} {books_data['count']} tadan\n\n"
                    
        except:
            if books_data['next']:
                text = f"Natijalar 20-30 {books_data['count']} tadan\n\n"
            else:
                text = f"Natijalar 10-{books_data['count']} {books_data['count']} tadan\n\n"
                
    else:
        text = f"Natijalar 1-{books_data['count']} {books_data['count']} tadan\n\n"
             
    for i, book in enumerate(books_data['results'], start=1):
        if book['document_filename']:
            text += f"""{i}. <i>{book['document_filename'][0:60].strip()}</i>  {random.choice(books)}\n"""
        else:
            text += """{}. {}  {}\n""".format(i, book['description'][0:60].strip().replace('\n', ''), random.choice(books))
            
        button = types.InlineKeyboardButton(text=i, callback_data=f"book__{book['file_link']}")
        keyboard.insert(button)
    
    if books_data['next']:
        next_page_link = books_data['next'].split('?')[1]
    else:
        next_page_link = ''
        
    next_page_button = types.InlineKeyboardButton(text="⏭️", callback_data=f"next_page_link__{next_page_link}")
        
    if books_data['previous']:
        prev_page_link = books_data['previous'].split('?')[1]
    else: 
        prev_page_link = ''
        
    prev_page_button = types.InlineKeyboardButton(text="⏮️", callback_data=f"prev_page_link__{prev_page_link}")

    keyboard.insert(prev_page_button)
    keyboard.insert(next_page_button)

    return (keyboard, text)
    
def get_keyboards(query):
    books_data = get_books_data(query=query)

    
    if books_data:
        if books_data['count'] > 0:
            keyboards = keyboard(books_data=books_data)
            return (keyboards[1], 200, keyboards[0], books_data)
            # await bot.send_message(text="Kitaplar:", reply_markup=keyboard)
        else:
            text = "🙇 Afsuski bunday kitob topilmadi, iltimos kitob nomini tekshirib ko'ring"
            return (text, 404)
    else:
        text = "🙇 Iltimos qayta urunib ko'ring."
        return (text, 405)
    


async def update_message(message: types.Message, new_value: str, keyboard: json):
    with suppress(MessageNotModified):
      await message.edit_text(text=new_value, reply_markup=keyboard)  
        
data = tuple

@dp.message_handler(state=None)
async def search(message: types.Message, state=FSMContext):
    data = get_keyboards(message.text)
    text = data[0]
    status_code = data[1]
    try:
        keyboard = data[2]
        await state.update_data(data[3])
    except:
        pass

    
    if status_code == 200:
        await message.answer(text, reply_markup=keyboard)
    else:
        await message.answer(text)
           

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('book_'))
async def process_book_button(callback_query: types.CallbackQuery, state=FSMContext):
    book_link = callback_query.data.split('__')[1]
    data = await state.get_data()
    bookMenu = types.InlineKeyboardMarkup(row_width=2)
    await callback_query.message.answer_document(document="https://t.me/vkm_book_baza/117680")
    if data:
        for obj in data['results']:
            if obj['file_link'] == book_link:
                favorites_btn = types.InlineKeyboardButton(text="❤️/💔", callback_data=f"favorites_btn__{book_link}")
                delete_mgs_btn = types.InlineKeyboardButton(text="❌", callback_data="delete_msg")
                bookMenu.insert(favorites_btn)
                bookMenu.insert(delete_mgs_btn)
                await callback_query.message.answer_document(caption=obj['description'].replace('\n', ''), document=book_link, reply_markup=bookMenu)
                
        await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('next_page_'))
async def change_page(query: types.CallbackQuery):
    if query.data.split('__')[1] == '':
        await query.answer(text="Sahifalar tugadi")
    
    else:
        
        next_page_link = link + query.data.split('__')[1]
        data = make_query(next_page_link)
        keyboards = keyboard(data)
    
        await update_message(message=query.message, new_value=keyboards[1], keyboard=keyboards[0] )

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('prev_page_'))
async def change_page(query: types.CallbackQuery):

    if query.data.split('__')[1] == "":
        await query.answer(text="Siz allaqachon birinchi sahifadasiz!")
    else:
        prev_page_link = link + query.data.split('__')[1]
        data = make_query(prev_page_link)
        keyboards = keyboard(data)
        
        await update_message(message=query.message, new_value=keyboards[1], keyboard=keyboards[0])
        
@dp.callback_query_handler(text_contains="favorites_btn")
async def add_rm_fv_books(callback_query: types.CallbackQuery, state=FSMContext):
    user_telegram_id = callback_query.from_user.id
    document_filename = callback_query.message.document.file_name
    document_link = callback_query.data.split('__')[1]
    print(document_link)
    
    user_books = await db.get_favorite_books(telegram_id=user_telegram_id)

    # print(user_books['favorite_books'])
    favorite_books = {document_filename : document_link}
    if user_books['favorite_books']:
        user_books = json.loads(user_books[0])
        if not(document_filename in user_books):
            user_books.update({document_filename: document_filename})
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

    
    # await call.message.delete()
    # await call.answer(cache_time=60)
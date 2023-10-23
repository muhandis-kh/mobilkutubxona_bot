import re
from korrektor_py import Korrektor
from data.config import TOKEN, KORREKTOR_TOKEN
import requests
from aiogram import types
from random import randrange
from urllib.parse import quote
from loader import dp
import random


korrektor = Korrektor(KORREKTOR_TOKEN)

alphabet = "latin"

# Matn kirill alifbosida ekanligini tekshiruvchi funksiya
def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


# kelgan lingda request yuborish uchun funksiya
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
        print(f"Error code: {response.status_code} {response}")

# Text oqrali kitob ma'lumotlarini oluvchi funksiya
def get_books_data(query):
    
    # Korrektor API ishlamayotganligi sababli kodning bu qismi o'chirib qo'yildi
    # if has_cyrillic(query):
    #     result = korrektor.transliterate(alphabet, query)
    #     encoded_query = quote(result.text)
    # else:
        # kelgan textni browser formatiga o'tkazish uchun
        encoded_query = quote(query)


        # URL
        api_url = f"https://mlibrary.up.railway.app/api/file-book-api/?search={encoded_query}&status=True"

        return make_query(api_url)


# Kelgan kitob ma'lumotlari asosida tugmalar va kitob nomlarini hosil qilish uchun 
def get_keyboards_and_text(books_data):
    books = ["📔", "📕", "📖", "📗", "📘", "📙", "📚", "📑", "🔖", "🧾"]
    
    # Ma'lumot uzunligiga ko'ra tugmalar joylashuvi uchun
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
        
    
    # Kelgan datada keyingi sahifa uchun link bo'lsa
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
            #\n f-string ichida ishlatib bo'lmagani uchun Python 2 sintax sidan foydalananildi
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
  
# Yuqoridagi funksiyalar orqali ma'lumotlarni yuboruvchi funksiya   
def get_data(query):
    books_data = get_books_data(query=query)

    
    if books_data:
        if books_data['count'] > 0:
            keyboards_and_text = get_keyboards_and_text(books_data=books_data)
            return (keyboards_and_text[1], 200, keyboards_and_text[0], books_data)
            # await bot.send_message(text="Kitaplar:", reply_markup=keyboard)
        # So'rov bo'yicha kitob topilmaganda yuboriladigan text
        else:
            text = "🙇 Afsuski bunday kitob topilmadi, iltimos kitob nomini tekshirib ko'ring"
            return (text, 404)
    # Internet bilan bog'liq hatolik yuzaga kelganida yuboriladigan text
    else:
        text = "🙇 Iltimos qayta urunib ko'ring."
        return (text, 405)
    

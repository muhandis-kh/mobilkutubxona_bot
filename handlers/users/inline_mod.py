from aiogram import types
from loader import dp
from .functions import get_books_data, make_query
import time
from pprint import pprint

@dp.inline_handler()
async def empty_query(query: types.InlineQuery):
    
    if query.query and len(query.query) > 3:
        time.sleep(2)
        books_data = get_books_data(query=query.query)
        results = []
        if books_data['results']:
            for book in books_data['results']:
                results.append(
                    types.InlineQueryResultDocument(
                        id=book['id'],
                        title=book['document_filename'] if book['document_filename'] else book['description'][0:60].replace('\n', ''),
                        mime_type="application/pdf",
                        document_url=book['file_link'],
                        description=book['description'],
                        caption=book['description'],
                        ),
                )
            await query.answer(results=results)
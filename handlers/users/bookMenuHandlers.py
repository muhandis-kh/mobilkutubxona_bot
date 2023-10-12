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
from keyboards.inline.inline import bookMenu
import logging

@dp.callback_query_handler(text_contains="favorites_btn")
async def add_rm_fv_books(call: types.CallbackQuery):
    callback_data = call.data
    logging.info(f"{callback_data=}")
    # await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Kitoblar", reply_markup=booksMenu)
    await call.message.delete()
    await call.answer(cache_time=60)
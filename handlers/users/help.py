from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("/start - Botni qayta ishga tushurish\n/kutubxonam - Tanlangan kitoblar ro'yhati\n\nYordam uchun <a href='https://t.me/khojimirzayev'>men</a> bilan bog'laning")
    
    await message.answer("\n".join(text))

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

bookMenu = InlineKeyboardMarkup(
    inline_keyboard=[
    [
        InlineKeyboardButton(text="❤️/💔", callback_data="favorites_btn"),
        InlineKeyboardButton(text="❌", callback_data="delete_msg"),
    ],
])
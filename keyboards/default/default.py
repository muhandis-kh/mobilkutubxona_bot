from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

random_book = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="🎲 Tasodifiy kitob")],
    ],
    resize_keyboard=True,
)

message_to_user = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="Userga xabar yuborish")],
    ],
    resize_keyboard=True,
)

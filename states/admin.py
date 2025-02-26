from aiogram.dispatcher.filters.state import StatesGroup, State

class AdminState(StatesGroup):
    message_to_user = State()
    message_to_user_file = State()
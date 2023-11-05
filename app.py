from aiogram import executor

from loader import dp, db, bot
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from data.config import ADMINS


async def on_startup(dispatcher):
    try:
            await db.create()
            await db.create_table_users()       
    except Exception as e:
        msg = f"Database ni yaratishda xatolik yuzaga keldi: {e}"
        await bot.send_message(chat_id=ADMINS[0], text=msg)
        print(e)
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

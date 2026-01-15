# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo

# === НАЛАШТУВАННЯ ===
TOKEN = "8500498661:AAF2TTOlCi_nIg346hOqwLgVdEXN3vSapSo" 
# Сюди вставимо HTTPS посилання, яке дасть ngrok (див. крок 6)
WEB_APP_URL = "https://google.com" 

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Створюємо кнопку, яка відкриває наш сайт всередині Телеграм
    kb = [
        [types.KeyboardButton(text="🚗 Моніторинг черг", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    await message.answer(
        "Привіт! Я моніторю кордон України.\n"
        "Натисни кнопку нижче, щоб побачити ситуацію онлайн.", 
        reply_markup=keyboard
    )

async def main():
    print("Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
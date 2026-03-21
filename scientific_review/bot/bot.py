# bot/bot.py
import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем роутеры и состояния
from .handlers.start import router as start_router
from .handlers.upload import router as upload_router
from .handlers.states import UserStates

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Установите BOT_TOKEN в .env файле!")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключаем роутеры
dp.include_router(start_router)
dp.include_router(upload_router)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Бот запущен по ТЗ...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio  
from aiogram import Bot, Dispatcher  
from ..config.settings import TG_TOKEN
from ..bot.handlers import start, upload

bot = Bot(token=TG_TOKEN)  
dp = Dispatcher()  

dp.include_router(start.router)
dp.include_router(upload.router)


async def main():  
    await dp.start_polling(bot)  

if __name__ == "__main__":  
    asyncio.run(main())
    
import asyncio  
from aiogram import Bot, Dispatcher  
from config import settings
import handlers 

bot = Bot(token=TOKEN)  
dp = Dispatcher()  

dp.include_router(handlers.router)  


async def main():  
    await dp.start_polling(bot)  

if __name__ == "__main__":  
    asyncio.run(main())
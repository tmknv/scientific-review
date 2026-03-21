from aiogram import Router
from aiogram.types import Message, Document
import aiohttp

router = Router()

API_URL = "http://localhost:8000/upload_paper"

@router.message(lambda message: message.document)
async def handle_pdf(message: Message):
    doc: Document = message.document

    file = await message.bot.get_file(doc.file_id)
    file_path = file.file_path

    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}"

    await message.answer("Обрабатываю статью... ⏳")

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json={"file_url": file_url}) as resp:
            result = await resp.json()

    await message.answer(format_result(result))
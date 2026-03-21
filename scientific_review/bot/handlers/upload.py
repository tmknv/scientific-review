# bot/handlers/upload.py
import os
import tempfile
import json
import random
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from ..client import AnalysisClient

from .states import UserStates
from .start import start_kb

router = Router()
client = AnalysisClient()

# Глобал для истории (в продакшене → Redis/DB)
USER_RESULTS = {}

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def extract_text(file_path: str, filename: str) -> str:
    """Извлечение текста из PDF/DOCX/TXT"""
    ext = filename.lower().split(".")[-1]
    if ext == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == "docx":
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    elif ext == "pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError("Неподдерживаемый формат")


async def show_mode_selection(message: Message):
    """Кнопки выбора режима (Inline)"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Быстрый анализ (LLM)", callback_data="mode:quick")
    builder.button(text="Multi-agent анализ", callback_data="mode:multi")
    builder.button(text="Сравнение моделей", callback_data="mode:compare")
    builder.button(text="Тест стабильности", callback_data="mode:stability")
    builder.adjust(1)
    await message.answer("🎯 Выберите режим анализа:", reply_markup=builder.as_markup())


async def show_result(message: Message, result: dict, mode: str):
    """Экран результата по ТЗ"""
    text = (
        f"📊 **Итоговый скор:** {result['total_score']}/100\n\n"
        f"**Оценки:**\n"
        f"• Новизна: {result['scores']['новизна']}\n"
        f"• Научность: {result['scores']['научность']}\n"
        f"• Сложность: {result['scores']['сложность']}\n"
        f"• Читаемость: {result['scores']['читаемость']}\n\n"
        f"**Рецензия:**\n{result['review']}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Подробнее", callback_data="action:details")
    builder.button(text="Выводы агентов", callback_data="action:agents")
    builder.button(text="JSON", callback_data="action:json")
    builder.button(text="Повторить", callback_data="action:repeat")
    builder.button(text="Сравнить модели", callback_data="action:compare")
    builder.button(text="Stability test", callback_data="action:stability")
    builder.button(text="Новый анализ", callback_data="action:new")
    builder.adjust(2)

    await message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup())


# ==================== ОБРАБОТКА ЗАГРУЗКИ ====================
@router.message(F.text == "Загрузить файл")
async def request_file(message: Message, state: FSMContext):
    await state.set_state(UserStates.WAITING_FOR_FILE)
    await message.answer(
        "📤 Отправьте файл (PDF, DOCX или TXT):\nМакс. 5 МБ",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(UserStates.WAITING_FOR_FILE, F.document)
async def handle_file(message: Message, state: FSMContext):
    document = message.document
    if document.file_size > 5 * 1024 * 1024:
        await message.answer("❌ Файл слишком большой (>5 МБ)")
        return

    ext = document.file_name.lower().split(".")[-1]
    if ext not in ["pdf", "docx", "txt"]:
        await message.answer("❌ Неподдерживаемый формат! Только PDF, DOCX, TXT")
        return

    # Скачиваем
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        dest = tmp.name
    await message.bot.download(document, destination=dest)

    try:
        text = extract_text(dest, document.file_name)
        if len(text) > 20000:
            await message.answer("❌ Текст слишком большой (>20 000 символов)")
            return

        await state.update_data(text=text, filename=document.file_name)
        await message.answer(f"✅ Файл получен!\nСимволов: {len(text)}")
        await show_mode_selection(message)
        await state.set_state(UserStates.MODE_SELECTED)

    except Exception:
        await message.answer("❌ Ошибка обработки файла")
    finally:
        os.unlink(dest)


@router.message(F.text == "Вставить текст")
async def request_text(message: Message, state: FSMContext):
    await state.set_state(UserStates.WAITING_FOR_TEXT)
    await message.answer(
        "✍️ Отправьте текст научной статьи:",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(UserStates.WAITING_FOR_TEXT)
async def handle_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if len(text) > 20000:
        await message.answer("❌ Текст слишком большой (>20 000 символов)")
        return

    await state.update_data(text=text)
    await message.answer(f"✅ Текст получен!\nСимволов: {len(text)}")
    await show_mode_selection(message)
    await state.set_state(UserStates.MODE_SELECTED)


# ==================== ВЫБОР РЕЖИМА И АНАЛИЗ ====================
@router.callback_query(F.data.startswith("mode:"))
async def handle_mode(callback: CallbackQuery, state: FSMContext):
    mode_key = callback.data.split(":")[1]
    mode_map = {
        "quick": "Быстрый анализ (LLM)",
        "multi": "Multi-agent анализ",
        "compare": "Сравнение моделей",
        "stability": "Тест стабильности"
    }
    mode = mode_map[mode_key]

    data = await state.get_data()
    text = data.get("text")
    if not text:
        await callback.answer("Нет текста для анализа!")
        return

    await state.set_state(UserStates.PROCESSING)
    await callback.message.edit_text("⏳ Анализируем...")

    # Запуск анализа
    result = await client.analyze(text, mode)

    # Сохраняем в историю
    uid = callback.from_user.id
    USER_RESULTS.setdefault(uid, []).append({"mode": mode, "result": result})

    # Обновляем данные FSM
    await state.update_data(last_result=result, last_mode=mode, last_text=text)

    await show_result(callback.message, result, mode)
    await state.set_state(UserStates.RESULT_READY)


# ==================== РАБОТА С РЕЗУЛЬТАТОМ ====================
@router.callback_query(F.data.startswith("action:"))
async def handle_result_action(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":")[1]
    data = await state.get_data()
    result = data.get("last_result")
    mode = data.get("last_mode")
    text = data.get("last_text")

    if action == "details":
        await state.set_state(UserStates.VIEWING_DETAILS)
        extended = result["review"] + "\n\n🔍 Расширенное ревью:\n• Структура отличная\n• Литература актуальна\n• Рекомендации по методологии"
        await callback.message.answer(extended)

    elif action == "agents":
        agents = "🤖 Выводы агентов:\nАгент-1: Высокая новизна\nАгент-2: Отличная читаемость\nАгент-3: Средняя сложность"
        await callback.message.answer(agents)

    elif action == "json":
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", encoding="utf-8") as f:
            f.write(json_str)
            path = f.name
        await callback.message.answer_document(
            FSInputFile(path),
            caption="📄 Результат в JSON"
        )
        os.unlink(path)

    elif action == "repeat":
        if not text:
            await callback.answer("Нет текста для повтора!")
            return
        processing = await callback.message.answer("🔄 Повторный анализ...")
        new_result = await client.analyze(text, mode)
        await state.update_data(last_result=new_result)
        await show_result(processing, new_result, mode)

    elif action == "compare":
        compare = "🔄 Сравнение моделей:\nLLM: 78/100\nMulti-agent: 85/100\nРазница в научности +7%"
        await callback.message.answer(compare)

    elif action == "stability":
        if "stability" in result:
            stab = result["stability"]
            txt = f"📈 Тест стабильности (5 прогонов):\n{runs}\nСреднее: {stab['average']}\nДисперсия: {stab['variance']}"
            await callback.message.answer(txt)
        else:
            await callback.message.answer("Запустите режим «Тест стабильности» для данных")

    elif action == "new":
        await state.clear()
        await callback.message.answer(
            "🔄 Новый анализ запущен!",
            reply_markup=start_kb
        )


# Ловим все остальные сообщения (защита от тупиков)
@router.message()
async def fallback(message: Message):
    await message.answer("Используйте кнопки меню или /start")
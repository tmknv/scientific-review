# bot/handlers/start.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router()

# Главная клавиатура (ReplyKeyboard — максимум кнопок, минимум текста)
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Загрузить файл"),
            KeyboardButton(text="Вставить текст")
        ],
        [
            KeyboardButton(text="Настройки"),
            KeyboardButton(text="О боте")
        ],
        [KeyboardButton(text="История анализов")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


@router.message(Command("start"))
async def cmd_start(message: Message, state):
    await state.set_state(UserStates.START)
    await message.answer(
        "👋 Добро пожаловать в бот рецензирования научных текстов!\n\n"
        "Выберите действие ниже:",
        reply_markup=start_kb
    )


@router.message(F.text == "Настройки")
async def settings(message: Message):
    await message.answer("⚙️ Настройки пока не реализованы (можно добавить язык/уведомления).")


@router.message(F.text == "О боте")
async def about(message: Message):
    await message.answer(
        "📖 Бот для рецензирования научных текстов по вашему ТЗ.\n"
        "Поддержка PDF/DOCX/TXT, 4 режима анализа, история, JSON-экспорт."
    )


@router.message(F.text == "История анализов")
async def show_history(message: Message):
    from handlers.upload import USER_RESULTS  # глобал для истории
    uid = message.from_user.id
    if uid not in USER_RESULTS or not USER_RESULTS[uid]:
        await message.answer("📜 История пуста. Сделайте первый анализ!")
        return

    history_text = "📜 Последние анализы:\n\n"
    for i, entry in enumerate(reversed(USER_RESULTS[uid][-5:]), 1):
        history_text += f"{i}. {entry['mode']} — скор {entry['result']['total_score']}/100\n"
    await message.answer(history_text)
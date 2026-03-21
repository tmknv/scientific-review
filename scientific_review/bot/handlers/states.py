# bot/handlers/states.py
from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    """FSM-состояния строго по ТЗ"""
    START = State()
    WAITING_FOR_FILE = State()
    WAITING_FOR_TEXT = State()
    MODE_SELECTED = State()
    PROCESSING = State()
    RESULT_READY = State()
    VIEWING_DETAILS = State()
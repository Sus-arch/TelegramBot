from aiogram.dispatcher.filters.state import StatesGroup, State


class Translate(StatesGroup):
    start_lang = State()
    end_lang = State()
    word = State()
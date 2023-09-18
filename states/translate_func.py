from aiogram.dispatcher.filters.state import State, StatesGroup


class Translate(StatesGroup):
    start_lang = State()
    end_lang = State()
    word = State()

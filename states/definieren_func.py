from aiogram.dispatcher.filters.state import StatesGroup, State


class Definition(StatesGroup):
    get_word = State()

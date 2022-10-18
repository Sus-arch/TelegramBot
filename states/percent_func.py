from aiogram.dispatcher.filters.state import StatesGroup, State


class Percent(StatesGroup):
    get_sentence = State()
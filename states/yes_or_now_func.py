from aiogram.dispatcher.filters.state import StatesGroup, State


class YesOrNo(StatesGroup):
    get_sentence = State()
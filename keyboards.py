from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


LANG = ['en', 'ru', 'ar', 'de', 'sp', 'fr', 'he', 'it', 'jp', 'du', 'po', 'pt', 'ro', 'se', 'tr', 'ua', 'ch']
button1 = KeyboardButton('/show_dog')
button2 = KeyboardButton('/show_cat')
button3 = KeyboardButton('/get_voice')
button4 = KeyboardButton('/translate')
button5 = KeyboardButton('/definieren')
button6 = KeyboardButton('/yes_or_no')
button7 = KeyboardButton('/get_percent')


main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2).row(button3, button4).row(button5, button6).row(button7)
lang_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*LANG)
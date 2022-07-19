from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


button1 = KeyboardButton('/show_dog')
button2 = KeyboardButton('/show_cat')
button3 = KeyboardButton('/get_voice')

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(button1, button2).row(button3)
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from states.voice_func import GetVoice
from states.translate_func import Translate
from utils import tranlate
import translators as ts
import os

import keyboards
from config import TOKEN
from requests import get


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def get_random_photo_cat():
    response = get('https://api.thecatapi.com/v1/images/search').json()
    file = response[0]['url']
    return file


async def get_random_photo_dog():
    response = get('https://dog.ceo/api/breeds/image/random').json()
    file = response['message']
    return file


async def handle_file(file: types.File, file_name: str, path: str):
    Path(f"{path}").mkdir(parents=True, exist_ok=True)
    await bot.download_file(file_path=file.file_path, destination=f"{path}/{file_name}")


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет", reply_markup=keyboards.main_keyboard)


@dp.message_handler(commands=['show_dog'])
async def send_dog(message: types.Message):
    file = await get_random_photo_dog()
    await message.answer(file)


@dp.message_handler(commands=['show_cat'])
async def send_cat(message: types.Message):
    file = await get_random_photo_cat()
    await message.answer(file)


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply("Отменено", reply_markup=keyboards.main_keyboard)


@dp.message_handler(commands=['get_voice'])
async def start_get_voice(message: types.Message):
    await GetVoice.S1.set()
    await message.reply("Отправьте голосовое сообщение и я сделаю из него mp3-файл")


@dp.message_handler(commands=['translate'])
async def start_translate(message: types.Message):
    await Translate.start_lang.set()
    await message.reply("Выберите начальный язык", reply_markup=keyboards.lang_keyboard)


@dp.message_handler(state=Translate.start_lang)
async def get_start_lang(message: types.Message, state: FSMContext):
    if message.text not in keyboards.LANG:
        await message.reply("Данный язык не предусмотрен", reply_markup=keyboards.lang_keyboard)
        return
    async with state.proxy() as data:
        data['s_lang'] = message.text

    await Translate.next()
    await message.reply("Выберите язык перевода", reply_markup=keyboards.lang_keyboard)


@dp.message_handler(state=Translate.end_lang)
async def get_end_lang(message: types.Message, state: FSMContext):
    if message.text not in keyboards.LANG:
        await message.reply("Данный язык не предусмотрен", reply_markup=keyboards.lang_keyboard)
        return
    async with state.proxy() as data:
        data['end_lang'] = message.text
    await Translate.next()
    await message.reply("Введите ваше слово")


@dp.message_handler(state=Translate.word)
async def get_word(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        translate_word = tranlate.translate(message.text, data['s_lang'], data['end_lang'])
        if not bool(translate_word):
            try:
                translate_word = ts.google(message.text, from_language=data['s_lang'], to_language=data['end_lang'])
            except:
                pass
        if bool(translate_word):
            await message.reply(translate_word, reply_markup=keyboards.main_keyboard)
        else:
            await message.reply("К сожалению данное слово не получилось перевести", reply_markup=keyboards.main_keyboard)
        await state.finish()


@dp.message_handler(state=GetVoice.S1, content_types=[types.ContentType.VOICE])
async def get_voice(message: types.Message, state: FSMContext):
    voice = await message.voice.get_file()
    path = "files/voices"
    name = f"{message.from_user.username}-audio.mp3"
    await handle_file(file=voice, file_name=name, path=path)
    audio = open(f'{path}/{name}', 'rb')
    await bot.send_audio(message.from_user.id, audio)
    os.remove(f"{path}/{name}")
    await state.finish()


@dp.message_handler(state=GetVoice.S1)
async def error_voice(message: types.Message):
    return await message.reply("Некорректный тип данных")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
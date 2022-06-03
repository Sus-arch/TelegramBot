import logging
from pathlib import Path
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
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


@dp.message_handler(content_types=[types.ContentType.VOICE])
async def get_voice(message: types.Message):
    voice = await message.voice.get_file()
    path = "files/voices"
    name = f"{message.from_user.username}-audio.mp3"
    await handle_file(file=voice, file_name=name, path=path)
    audio = open(f'{path}/{name}', 'rb')
    await bot.send_audio(message.from_user.id, audio)
    os.remove(f"{path}/{name}")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
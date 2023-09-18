import asyncio
import logging
import os
from pathlib import Path
from random import choice, randint

import translators as ts
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from requests import get

import keyboards
from config import TOKEN
from states.definieren_func import Definition
from states.percent_func import Percent
from states.translate_func import Translate
from states.voice_func import GetVoice
from states.yes_or_now_func import YesOrNo
from utils import get_definition, parseRZD, tranlate

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


@dp.message_handler(commands=['yes_or_no'])
async def start_yes_or_now(message: types.Message):
    await YesOrNo.get_sentence.set()
    await message.reply("Отправьте предложение и я скажу, правда это или нет")


@dp.message_handler(state=YesOrNo.get_sentence)
async def ret_yes_or_now(message: types.Message, state: FSMContext):
    await message.reply(choice(["Да", "Нет"]))
    await state.finish()


@dp.message_handler(commands=['get_percent'])
async def start_get_percent(message: types.Message):
    await Percent.get_sentence.set()
    await message.reply("Отправьте предложение и я скажу, на сколько процентов это правда")


@dp.message_handler(state=Percent.get_sentence)
async def get_percent(message: types.Message, state: FSMContext):
    await message.reply(f"{randint(0, 100)}%")
    await state.finish()


@dp.message_handler(commands=['translate'])
async def start_translate(message: types.Message):
    await Translate.start_lang.set()
    await message.reply("Выберите начальный язык", reply_markup=keyboards.lang_keyboard)


@dp.message_handler(commands=['definieren'])
async def start_defination(message: types.Message):
    await Definition.get_word.set()
    await message.reply("Отправьте слово на немецком языке, а я подскажу его значение")


@dp.message_handler(state=Definition.get_word)
async def get_word(message: types.Message, state: FSMContext):
    items = get_definition.definieren(message.text)
    if bool(items):
        text = ''
        if type(items) == list:
            for i, item in enumerate(items):
                text += f"{i + 1}. {item.strip()} \n"
        elif type(items) == str:
            text = items.strip()
        await state.finish()
        await message.reply(text, reply_markup=keyboards.main_keyboard)
    else:
        await state.finish()
        await message.reply("К сожалению я не могу назвать значение этого слова", reply_markup=keyboards.main_keyboard)


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
                translate_word = ''
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


async def periodical_task(time):
    while True:
        await asyncio.sleep(time)
        data = parseRZD.parse_tickest()
        if bool(data):
            message = 'НАЙДЕН БИЛЕТ \n'
            s_plac = 0
            s_kupe = 0
            for num, ticket in enumerate(data):
                message += f'{num + 1}. Время - {ticket["time"]} \n'
                if ticket["plac"]["count"] != 0:
                    message += f'Плацкарт ({ticket["plac"]["count"]} шт.) - {ticket["plac"]["price"]} \n'
                    s_plac = max(int(ticket["plac"]["count"]), s_plac)
                if ticket["kupe"]["count"] != 0:
                    message += f'Купе ({ticket["kupe"]["count"]} шт.) - {ticket["kupe"]["price"]} \n'
                    s_kupe = max(int(ticket["kupe"]["count"]), s_kupe)
                message += f'Ссылка - {ticket["link"]} \n'
                message += '-' * 40 + '\n'
                if s_plac >= 2 or s_kupe >= 2:
                    await bot.send_message("609673774", message)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(periodical_task(600))
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)

import requests
from bs4 import BeautifulSoup

LANGUAGES = {
    'en': 'english',
    'ru': 'russian',
    'ar': 'arabic',
    'de': 'german',
    'sp': 'spanish',
    'fr': 'french',
    'he': 'hebrew',
    'it': 'italian',
    'jp': 'japanese',
    'du': 'dutch',
    'po': 'polish',
    'pt': 'portuguese',
    'ro': 'romanian',
    'se': 'swedish',
    'tr': 'turkish',
    'ua': 'ukrainian',
    'ch': 'chinese'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}


def get_content(response):
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find('div', id='translations-content').find('a', class_='translation ltr dict n').find('span', class_='display-term').get_text()
        return items
    except AttributeError:
        return None


def translate(text, s_lang, end_lang):
    if s_lang in LANGUAGES.keys() and end_lang in LANGUAGES.keys() and bool(text):
        link = f"https://context.reverso.net/translation/{LANGUAGES[s_lang]}-{LANGUAGES[end_lang]}/{text}"
        response = requests.get(link, headers=HEADERS)
        if response:
            return get_content(response)
    return None

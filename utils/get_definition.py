import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}


def get_response(link, headers=''):
    response = requests.get(link, headers=HEADERS)
    return response


def get_content(response, state=0):
    try:
        if state == 0:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find(class_='vignette').find(class_='vignette__link').get('href')
        elif state == 1:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find('div', class_='division', id='bedeutungen').find_all('div', class_='enumeration__text')
            items = [item.get_text() for item in items]
        return items
    except AttributeError:
        if state == 1:
            try:
                items = soup.find('div', class_="division", id='bedeutung').find('p').get_text()
            except AttributeError:
                return None
            else:
                return items
        else:
            return None


def definieren(word):
    response = get_response(f'https://www.duden.de/suchen/dudenonline/{word}', headers=HEADERS)
    if response:
        new_link = get_content(response)
        response = get_response(f"https://www.duden.de{new_link}", headers=HEADERS)
        return get_content(response, state=1)

from bs4 import BeautifulSoup
from selenium import webdriver
import time


LINK_FRIST = 'https://ticket.rzd.ru/searchresults/v/1/5a3244bc340c7441a0a556ca/5a13baf9340c745ca1e80436/2023-08-03'
LINK_SECOND = 'https://ticket.rzd.ru/searchresults/v/1/5a3244bc340c7441a0a556ca/5a13baf9340c745ca1e80436/2023-08-04'


def get_source_html(url):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    driver.get("http://www.python.org")

    try:
        driver.get(url=url)
        time.sleep(5)

        with open('index_selenium.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)

        with open('index_selenium.html', encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')
        card = soup.find('div', class_='row card__body ng-star-inserted')
        try:
            plaz_count = card.find_all('div', class_="card-class__quantity ng-star-inserted")[0].get_text().strip()
            plaz_price = card.find_all('div', class_="card-class__price")[0].get_text().replace('\xa0', '')
        except:
            plaz_count = 0
            plaz_price = None
        try:
            kupe_count = card.find_all('div', class_="card-class__quantity ng-star-inserted")[1].get_text().strip()
            kupe_price = card.find_all('div', class_="card-class__price")[1].get_text().replace('\xa0', '')
        except:
            kupe_count = 0
            kupe_price = None
        time_vag = card.find('div', class_="card-route__date-time card-route__date-time--from").get_text() + '||' + card.find('div', class_="card-route__date-time card-route__date-time--to").get_text()

        data = {
            'time': time_vag,
            'plac': {
                'count': plaz_count,
                'price': plaz_price
            },
            'kupe': {
                'count': kupe_count,
                'price': kupe_price
            }
        }
        return data

    except Exception as _ex:
        return _ex
    finally:
        driver.close()
        driver.quit()


def parse_tickest():
    data = []
    first_data = get_source_html(LINK_FRIST)
    if bool(first_data):
        first_data['link'] = LINK_FRIST
        data.append(first_data)
    second_data = get_source_html(LINK_SECOND)
    if bool(second_data):
        second_data['link'] = LINK_SECOND
        data.append(second_data)

    return data

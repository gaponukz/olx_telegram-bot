import requests
from bs4 import BeautifulSoup

async def parse_urls(url: str) -> list:
    response = requests.get(url)
    html = BeautifulSoup(response.text, 'html.parser')

    urls = html.find_all('a', {'class': 'marginright5 link linkWithHash detailsLink'})

    return [url.get('href') for url in urls][:5]

async def parse(url: str) -> dict:
    response = requests.get(url)
    html = BeautifulSoup(response.text, 'html.parser')

    return {
        'url': url,
        'img': html.find('div', {'class': 'descgallery__image'}).find('img').get('src'),
        'description': clean(html.find('div', {'class': 'clr lheight20 large'}).text),
        'title': clean(html.select('#offerdescription > div.offer-titlebox > h1')[0].text),
        'price': html.select('#offerdescription > div.offer-titlebox > div.offer-titlebox__price > div > strong')[0].text
    }

async def get_heading(url: str) -> str:
    response = requests.get(url)
    html = BeautifulSoup(response.text, 'html.parser')
    try:
        return html.select('#main-category-choose-label')[0].text
    except:
        return None

def clean(text: str) -> str:
    return text.replace('\t', ' ').replace('\n', ' ').strip()